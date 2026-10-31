"""Loopback dashboard over the existing registry, jobs and package files."""

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import re
import shutil
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import urlopen

from .agent import cycle, registry_path
from .core import (Context, ReleaseError, atomic_json, digest, host_name, inside,
                   lock, read_json, verify_runtime, discover, hidden_flags)

PORT = 8877
PRODUCT = "AI11 Local Builds"
SCAN_SECONDS = 30
SYNC_IDLE_SECONDS = 300
SYNC_ACTIVE_SECONDS = 60


def identity(registry):
    return hashlib.sha256(str(registry.resolve()).encode()).hexdigest()


class Dashboard:
    def __init__(self, registry):
        self.registry = registry.resolve()
        self.token = secrets.token_urlsafe(32)
        self.guard = threading.Lock()
        self.children = {}

    def projects(self):
        return read_json(self.registry)["projects"]

    def scan(self):
        for name, project in self.projects().items():
            if not project.get("enabled") or host_name() not in project["hosts"]:
                continue
            root = Path(project["catalogue"])
            queue = root / (name + "-queue.json")
            if not queue.exists():
                continue
            data = discover(Path(project["repo"]), root, queue)
            if data["enabled"]:
                try:
                    with lock(root / ".worker.lock"):
                        pass
                except ReleaseError:
                    continue
                from .cli import spawn_worker
                spawn_worker(queue)

    def jobs(self, project):
        root = Path(project["catalogue"]) / "releases" / project["project"]
        directories = {path.parent for pattern in ("*/*/manifest.json", "*/*/job.json") for path in root.glob(pattern)
                       if path.resolve().is_relative_to(root.resolve())}
        def order(directory):
            version = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)\+(\d+)", directory.parent.name)
            numbers = tuple(int(value) for value in version.groups()) if version else (0, 0, 0, 0)
            return (*numbers, directory.name)
        # Include prepared jobs in the same numeric order as archived releases.
        yield from sorted(directories, key=order, reverse=True)

    def find(self, name, sha):
        project = self.projects().get(name)
        if not project:
            raise ReleaseError("Unknown registered project")
        for directory in self.jobs(project):
            if directory.name == sha:
                return project, directory
        raise ReleaseError("Unknown release SHA")

    def busy(self, directory):
        try:
            with lock(directory / ("." + host_name() + ".lock")):
                return False
        except ReleaseError as error:
            if str(error).startswith("Busy operation:"):
                return True
            raise

    def state(self):
        projects = []
        for name, project in sorted(self.projects().items()):
            releases = []
            for directory in self.jobs(project):
                try:
                    manifest = read_json(directory / "manifest.json") if (directory / "manifest.json").exists() else {}
                    job = read_json(directory / "job.json") if (directory / "job.json").exists() else None
                    source = job or manifest
                    query = {"project": name, "sha": directory.name}
                    files = []
                    for group in ("packages", "unverified_packages"):
                        for filename, record in manifest.get(group, {}).items():
                            path = inside(directory, record["path"])
                            files.append({"name": filename, "size": record["size"], "sha256": record["sha256"],
                                "present": path.is_file(), "verified": group == "packages",
                                "url": "/api/file?" + urlencode({**query, "package": filename})})
                    hosts = {}
                    active = self.busy(directory) if job else False
                    for role in (job or {}).get("required_steps", {}):
                        result = directory / "results" / (role + ".json")
                        value = read_json(result) if result.exists() else {"status": "waiting", "steps": {}}
                        status = value["status"]
                        if role == host_name() and status == "running" and not active:
                            status = "interrupted"
                        hosts[role] = {"status": status, "step": value.get("current_step"),
                            "error": value.get("steps", {}).get(value.get("current_step"), {}).get("error") or value.get("error"), "updated": value.get("updated"),
                            "runtime_revision": value.get("runtime_revision"),
                            "attempt_runtime_revision": value.get("attempt_runtime_revision", value.get("runtime_revision")),
                            "pending_runtime_revision": value.get("pending_runtime_revision"),
                            "steps": [{"name": key, **{k: v for k, v in row.items() if k in
                                ("status", "started", "finished", "error")}} for key, row in value.get("steps", {}).items()],
                            "missing": [s for s in job["required_steps"][role] if value.get("steps", {}).get(s, {}).get("status") != "passed"]}
                    logs = [{"name": p.relative_to(directory).as_posix(), "size": p.stat().st_size,
                             "url": "/api/file?" + urlencode({**query, "log": p.relative_to(directory).as_posix()})}
                            for p in sorted((directory / "logs").glob("*/*.log")) if p.resolve().is_relative_to(directory.resolve())]
                    publication_path = directory / "publication.json"
                    publication = read_json(publication_path) if publication_path.exists() else {}
                    published = publication.get("published") is True
                    if published:
                        for value in hosts.values():
                            if value["missing"]:
                                value.update(status="published", missing=[], error=None, step=None,
                                             pending_runtime_revision=None, verified_elsewhere=True)
                    waiting = {name: value["missing"] for name, value in hosts.items() if value["missing"]}
                    waiting_hosts = [name for name in waiting if name != host_name()]
                    status = "published" if published else "running" if active else manifest.get("status", "prepared")
                    if not published and not active and waiting_hosts and host_name() in hosts and not hosts[host_name()]["missing"]:
                        status = "waiting_other_hosts"
                    expected_files = (job or {}).get("artifacts", list(manifest.get("packages", {})))
                    releases.append({"sha": directory.name, "version": source["version"], "build": source["build"],
                        "status": status, "files": files, "hosts": hosts,
                        "logs": logs, "controllable": bool(job) and not published, "active": active,
                        "waiting_checks": waiting, "waiting_hosts": waiting_hosts, "expected_packages": len(expected_files),
                        "missing_packages": [name for name in expected_files if name not in manifest.get("packages", {})],
                        "publication": {"published": published, "url": publication.get("url"),
                                        "waiting": publication.get("waiting") if not published else None},
                        "stop_requested": (directory / "stop-request.json").exists(),
                        "runtime_revision": (job or {}).get("preparation_revision"),
                        "protocol": (job or {}).get("protocol_version", 1) if job else None})
                except (OSError, ValueError, KeyError, ReleaseError) as error:
                    releases.append({"sha": directory.name, "error": str(error), "files": [], "hosts": {}, "logs": []})
            queue = Path(project["catalogue"]) / (name + "-queue.json")
            q = read_json(queue) if queue.exists() else {}
            projects.append({"name": name, "enabled": project.get("enabled"), "hosts": project["hosts"],
                "automatic_builds": q.get("enabled", False), "queue": q.get("commits", {}), "releases": releases})
        agent = self.registry.parent / (host_name() + "-agent-result.json")
        failure = self.registry.parent / "service-error.json"
        return {"product": PRODUCT, "host": host_name(), "token": self.token, "time": time.time(),
                "projects": projects, "agent": read_json(agent) if agent.exists() else None,
                "sync_error": read_json(failure).get("error") if failure.exists() else None}

    def action(self, name, sha, action):
        if action not in ("start", "retry", "restart", "stop"):
            raise ReleaseError("Unknown action")
        project, directory = self.find(name, sha)
        if not (directory / "job.json").is_file():
            raise ReleaseError("Archived releases have no runnable job")
        job = read_json(directory / "job.json")
        if host_name() not in job["required_steps"]:
            raise ReleaseError("This job does not target this operating system")
        publication = directory / "publication.json"
        if publication.exists() and read_json(publication).get("published"):
            raise ReleaseError("Published releases are immutable")
        with self.guard:
            key = (name, sha)
            child = self.children.get(key)
            active = self.busy(directory) or bool(child and child.poll() is None)
            if action in ("stop", "restart"):
                atomic_json(directory / "stop-request.json", {"requested": time.time(), "source": "localhost dashboard"})
                if action == "stop":
                    return {"status": "stopping" if active else "stopped"}
                if active:
                    threading.Thread(target=self.restart_after_stop, args=(name, sha), daemon=True).start()
                    return {"status": "restarting"}
            elif active:
                raise ReleaseError("This job is already running")
            verify_runtime(directory)
            directory.joinpath("stop-request.json").unlink(missing_ok=True)
            python = Path(sys.executable)
            if python.name.lower() == "pythonw.exe":
                python = python.with_name("python.exe")
            command = [str(python), "-u", str(directory / "runtime/local_release/cli.py"), "run", "--job", str(directory),
                       "--config", project["config"], "--publish"]
            output = directory / "logs" / host_name() / "dashboard-worker.log"
            output.parent.mkdir(parents=True, exist_ok=True)
            options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
            with output.open("a", encoding="utf-8") as stream:
                self.children[key] = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, **options)
            return {"status": "starting"}

    def restart_after_stop(self, name, sha):
        # Cooperative shutdown allows fixture restoration and result transfer.
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            _, directory = self.find(name, sha)
            child = self.children.get((name, sha))
            if not self.busy(directory) and (not child or child.poll() is not None):
                self.action(name, sha, "retry")
                return
            time.sleep(0.3)

    def file(self, query):
        project, directory = self.find(query["project"], query["sha"])
        if "package" in query:
            manifest = read_json(directory / "manifest.json")
            record = {**manifest.get("packages", {}), **manifest.get("unverified_packages", {})}.get(query["package"])
            if not record:
                raise ReleaseError("Unknown package")
            path = inside(directory, record["path"])
            if digest(path) != record["sha256"]:
                raise ReleaseError("Package digest differs from its manifest")
            return path, None
        relative = query.get("log", "")
        path = inside(directory, relative)
        if not relative.startswith("logs/") or path.suffix != ".log" or not path.is_file():
            raise ReleaseError("Only registered packages and build logs are downloadable")
        # Display the tail, with the host's actual configured secrets redacted.
        config = read_json(Path(project["config"]))
        ctx = Context(directory, config) if (directory / "job.json").exists() else None
        if ctx:
            # Reading a log must not rewrite a builder's credential files.
            values = []
            for field in ("defines_file", "sentry_properties", "github_token_file"):
                source = Path(config[field]) if config.get(field) else None
                if not source or not source.is_file():
                    continue
                content = source.read_text(encoding="utf-8").strip()
                if field == "defines_file":
                    values.extend(str(v) for v in json.loads(content).values())
                elif field == "sentry_properties":
                    values.extend(re.findall(r"(?m)^auth_token\s*[=:]\s*(.+)$", content))
                else:
                    values.append(content)
            ctx.refresh_redaction(values)
        with path.open("rb") as stream:
            stream.seek(max(0, path.stat().st_size - 512 * 1024))
            value = stream.read().decode("utf-8", errors="replace")
        return path, (ctx.redact(value) if ctx else value).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "AI11LocalBuilds/1"

    def log_message(self, *_):
        pass

    def respond(self, status, value, kind="application/json; charset=utf-8"):
        content = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(content)

    def valid_host(self):
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def do_GET(self):
        if not self.valid_host():
            self.respond(403, {"error": "Invalid loopback Host"})
            return
        try:
            url = urlsplit(self.path)
            if url.path == "/api/health":
                self.respond(200, {"product": PRODUCT, "registry": identity(self.server.dashboard.registry)})
            elif url.path == "/api/state":
                self.respond(200, self.server.dashboard.state())
            elif url.path in ("/", "/dashboard.js", "/dashboard.css", "/favicon.svg"):
                names = {"/": ("dashboard.html", "text/html"), "/dashboard.js": ("dashboard.js", "text/javascript"),
                         "/dashboard.css": ("dashboard.css", "text/css"), "/favicon.svg": ("favicon.svg", "image/svg+xml")}
                name, kind = names[url.path]
                self.respond(200, Path(__file__).with_name(name).read_bytes(), kind + "; charset=utf-8")
            elif url.path == "/api/file":
                query = {k: v[0] for k, v in parse_qs(url.query).items()}
                path, content = self.server.dashboard.file(query)
                if content is not None:
                    self.respond(200, content, "text/plain; charset=utf-8")
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + __import__("urllib.parse", fromlist=["quote"]).quote(path.name))
                    self.send_header("Content-Length", str(path.stat().st_size))
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    with path.open("rb") as stream:
                        shutil.copyfileobj(stream, self.wfile)
            else:
                self.respond(404, {"error": "Unknown resource"})
        except (OSError, ValueError, KeyError, ReleaseError) as error:
            self.respond(400, {"error": str(error)})

    def do_POST(self):
        expected_origin = f"http://127.0.0.1:{self.server.server_port}"
        if not self.valid_host() or self.headers.get("Origin") not in (None, expected_origin) or not secrets.compare_digest(
                self.headers.get("X-AI11-Token", ""), self.server.dashboard.token):
            # Drain a bounded rejected body so Windows does not reset the TCP
            # connection before the browser receives the 403 response.
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if 0 < length <= 4096:
                    self.rfile.read(length)
            except ValueError:
                pass
            self.respond(403, {"error": "Control request requires this dashboard's token and origin"})
            return
        try:
            if self.path != "/api/action" or self.headers.get("Content-Type") != "application/json":
                raise ReleaseError("Expected JSON control request")
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 4096:
                raise ReleaseError("Invalid control payload length")
            value = json.loads(self.rfile.read(length))
            self.respond(200, self.server.dashboard.action(value["project"], value["sha"], value["action"]))
        except (OSError, ValueError, KeyError, ReleaseError) as error:
            self.respond(400, {"error": str(error)})


def make_server(registry, port=PORT):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    server.dashboard = Dashboard(registry)
    return server


def serve(registry, port=PORT, sync=True):
    registry = registry.resolve()
    with lock(registry.parent / ".service.lock"):
        server = make_server(registry, port)
        stop = registry.parent / "service-stop.json"
        stop.unlink(missing_ok=True)
        def scan():
            while not stop.exists():
                try:
                    if host_name() == "windows":
                        server.dashboard.scan()
                except Exception as error:
                    atomic_json(registry.parent / "discovery-error.json", {"time": time.time(), "error": str(error)})
                for _ in range(SCAN_SECONDS):
                    if stop.exists():
                        return
                    time.sleep(1)
        threading.Thread(target=scan, daemon=True).start()
        def observe():
            next_sync = 0
            while not stop.exists():
                if sync and host_name() == "windows" and time.monotonic() >= next_sync:
                    try:
                        cycle(registry, "windows")
                        (registry.parent / "service-error.json").unlink(missing_ok=True)
                    except Exception as error:
                        atomic_json(registry.parent / "service-error.json", {"time": time.time(), "error": str(error)})
                    active = any(server.dashboard.busy(directory) for project in server.dashboard.projects().values()
                                 for directory in server.dashboard.jobs(project) if (directory / "job.json").exists())
                    next_sync = time.monotonic() + (SYNC_ACTIVE_SECONDS if active else SYNC_IDLE_SECONDS)
                time.sleep(1)
            server.shutdown()
        threading.Thread(target=observe, daemon=True).start()
        atomic_json(registry.parent / "service.json", {"product": PRODUCT, "pid": os.getpid(), "url": f"http://127.0.0.1:{port}", "started": time.time()})
        try:
            server.serve_forever(poll_interval=0.3)
        finally:
            server.server_close()


def start(registry, port=PORT, sync=True):
    url = f"http://127.0.0.1:{port}"
    try:
        with urlopen(url + "/api/health", timeout=2) as response:
            health = json.load(response)
        if health != {"product": PRODUCT, "registry": identity(registry)}:
            raise ReleaseError("The fixed port is occupied by another service")
        return url
    except ValueError:
        raise ReleaseError("The fixed port answers with a different service") from None
    except OSError:
        pass
    python = Path(sys.executable)
    if os.name == "nt" and python.with_name("pythonw.exe").exists():
        python = python.with_name("pythonw.exe")
    argv = [str(python), str(Path(__file__).with_name("cli.py")), "serve", "--registry", str(registry), "--port", str(port)]
    if not sync:
        argv.append("--no-sync")
    options = {"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS} if os.name == "nt" else {"start_new_session": True}
    registry.parent.mkdir(parents=True, exist_ok=True)
    with (registry.parent / "service.log").open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, **options)
    for _ in range(50):
        try:
            with urlopen(url + "/api/health", timeout=1) as response:
                health = json.load(response)
            if health == {"product": PRODUCT, "registry": identity(registry)}:
                return url
            break
        except OSError:
            if process.poll() is not None:
                break
            time.sleep(0.2)
    raise ReleaseError("Local dashboard failed to start; inspect the private service.log for a port conflict")


def stop(registry, port=PORT):
    url = f"http://127.0.0.1:{port}/api/health"
    try:
        with urlopen(url, timeout=2) as response:
            health = json.load(response)
    except OSError:
        return
    if health != {"product": PRODUCT, "registry": identity(registry)}:
        raise ReleaseError("Refusing to stop a different service")
    atomic_json(registry.parent / "service-stop.json", {"stop": True})
    for _ in range(120):
        try:
            with urlopen(url, timeout=1):
                pass
        except OSError:
            return
        time.sleep(0.4)
    raise ReleaseError("Service is finishing a network operation; wait before restarting")


def install_startup(registry, port=PORT):
    if os.name != "nt":
        raise ReleaseError("Linux startup is installed by its graphical-login dispatcher")
    startup = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup/AI11 Local Builds.lnk"
    python = Path(sys.executable).with_name("pythonw.exe")
    if not python.is_file():
        raise ReleaseError("pythonw.exe is required for a hidden Windows startup service")
    cli = Path(__file__).with_name("cli.py").resolve()
    arguments = subprocess.list2cmdline([str(cli), "serve", "--registry", str(registry.resolve()), "--port", str(port)])
    # Structured environment avoids interpolating owner paths into PowerShell code.
    script = '''$s = New-Object -ComObject WScript.Shell
$link = $s.CreateShortcut($env:AI11_STARTUP_LINK)
if ((Test-Path -LiteralPath $env:AI11_STARTUP_LINK) -and $link.Description -ne 'AI11 Local Builds startup v1') { throw 'Unrelated startup shortcut exists' }
$link.TargetPath = $env:AI11_STARTUP_PYTHON
$link.Arguments = $env:AI11_STARTUP_ARGS
$link.WorkingDirectory = $env:AI11_STARTUP_CWD
$link.WindowStyle = 7
$link.Description = 'AI11 Local Builds startup v1'
$link.Save()
$check = $s.CreateShortcut($env:AI11_STARTUP_LINK)
if ($check.TargetPath -ne $env:AI11_STARTUP_PYTHON -or $check.Arguments -ne $env:AI11_STARTUP_ARGS) { throw 'Startup shortcut readback differs' }
'''
    env = dict(os.environ, AI11_STARTUP_LINK=str(startup), AI11_STARTUP_PYTHON=str(python),
               AI11_STARTUP_ARGS=arguments, AI11_STARTUP_CWD=str(cli.parent))
    result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], env=env, capture_output=True, creationflags=hidden_flags())
    if result.returncode:
        raise ReleaseError("Windows startup shortcut installation failed; existing unrelated shortcuts were preserved")
    atomic_json(registry.parent / "startup.json", {"path": str(startup), "target": str(python), "arguments": arguments, "url": f"http://127.0.0.1:{port}"})
    return startup
