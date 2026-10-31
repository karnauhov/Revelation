# Shared local build dashboard

Doc-Version: 1.1.0
Last-Updated: 2026-10-31
Source-Commit: working-tree

The owner's permanent local URL is **http://127.0.0.1:8877**.
The server binds only to loopback and reads one registry and existing catalogues. It displays
versions/builds/SHAs, platforms, checkpoints, errors and logs without copying packages.
Downloads verify the manifest SHA-256. Unverified packages differ from accepted packages.
Long stage names wrap inside their card, with separate positions for duration and status.
Platform cards stack on narrow screens. The current stage's actual error is shown instead
of the pipeline wrapper's summary; detailed history remains in the log.
Historical releases remain downloadable without build controls.
Completion of one OS is shown separately from readiness of the entire release. The panel lists
the specific required checks still missing and counts packages against the expected set.
After confirmed publication the status becomes Published, a GitHub link appears, and rebuild
controls are hidden. Local links continue to use the catalogue's single package files.
Newly prepared jobs and archives share numeric version/build ordering: 1.0.10 follows 1.0.9,
and build1000 follows999. A job appears as soon as it is prepared, before its first package or manifest.
When the current OS has passed its required checks and another OS remains pending, the status is Waiting for another OS.
The panel names that OS and preserves built packages until the corresponding builder's next login.

## Windows

The common registry is `%LOCALAPPDATA%/AI11/LocalRelease/registry.json`.
Revelation uses its canonical `.local-releases` and private `.local-releases/windows-config.json`.
This configuration is never served over HTTP. Install/restore from main:

```powershell
python scripts/local_release/release.py register-project --repo . --profile scripts/local_release/revelation.json --root .local-releases --config .local-releases/windows-config.json
python scripts/local_release/release.py install-service
```

The per-user `AI11 Local Builds.lnk` Startup shortcut launches `pythonw.exe` after login,
without a terminal or administrator rights. Installation reads back target/arguments and records
them in `startup.json` beside the registry. An unrelated same-name shortcut is preserved.
Git is checked every 30 seconds; after trigger activation, its hook delivers commits immediately.
Linux draft results are imported every 5 minutes while idle and every minute during a build.
The UI refreshes every 10 seconds while idle and every 3 seconds during a build; hidden tabs suspend polling.
GitHub finalization requires all gates; incomplete releases stay private. Automatic Windows
builds are enabled after the complete published REV301/build173 trial. Each new ordinary commit gets
the next build and its own queue entry; completed173 is never rebuilt.

Restart the server after updating main:

```powershell
python scripts/local_release/release.py stop-service
python scripts/local_release/release.py start-service
```

Shutdown is cooperative: wait for the process in `service.json` and HTTP responses to stop
before launching updated code. `start-service` reuses a live instance.
To remove startup, stop the server and delete only its marked shortcut from the user's Startup
folder. The registry, settings, logs and packages remain. A busy port is an error in the private
`service.log`; the occupying process remains untouched and the port never silently changes.

## Linux

One-time launch from the checkout:

```bash
git fetch origin
git switch main
git pull --ff-only
bash scripts/local_release/run-linux.sh
```

This installs `~/.config/autostart/ai11-local-builds.desktop`, the registry and version hook,
starts the same dashboard and runs the sequential dispatcher. Subsequent graphical logins open
an owned progress terminal, update main, receive runtime repairs and build registered Linux projects.
After its report the owner manually reboots to Windows. Remove the Desktop Entry to disable Linux
startup. No shared OS disk is required. Repeated automatic Ubuntu login, job receipt, the complete Linux trial
and automatic result return have been verified in the owner's real session.

## Controls

Start and retry resume checkpoints, retaining successful stages with verified outputs. Restart first
requests shutdown and waits for the builder. Stop applies only to the selected job: its coordinator
terminates its child process, restores integration fixtures and transfers diagnostics. Network calls
can delay shutdown. After service restart, the OS lock distinguishes live builds from interrupted
ones. An unavailable peer OS is shown as waiting.

POST requires the current dashboard token and valid Host/Origin; CORS is absent.
HTTP serves only manifest packages and redacted log tails up to 512 KiB. Configuration, keystores,
credentials and arbitrary paths are unavailable. UI values are rendered as text.

## Other projects

In that project's task, create its shared-engine profile, version helper, gates and gitignored
catalogue, then use `register-project` without a second server or package copies. For Linux add
an explicit `scripts/local_release/projects.json` entry: project, repository, directory, profile,
hosts and enabled. Arbitrary folders are never scanned. Each OS retains its own credentials.
Implement other projects' autobuilds in their corresponding tasks.

[OS exchange protocol](protocol.en.md) · [Release flow and gates](local-release.en.md).
