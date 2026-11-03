# Shared local build dashboard

Doc-Version: 1.3.2
Last-Updated: 2026-11-01
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
Measured stage time is immediately visible in each OS card, with the current stage updating while it runs.
New measurements use a monotonic clock, include retries and survive checkpoint invalidation. Nested integration
files are not added again to their parent timer. Waiting for another OS is excluded. Legacy started/finished
records are labelled estimates; ≥ indicates missing old measurements, including a reversed system clock.
This is measured stage time, rather than the interval between reboots.
Previously prepared jobs retain their pinned runtime and old timestamps. Exact monotonic measurements appear in new jobs or after an audited runtime update of an existing job.

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

## Delete a build

GitHub Releases use the actual job/manifest tag and verified source SHA, including auto tags.
Legacy false "GitHub deleted" records are reconciled through the unique project/SHA marker
without changing the confirmed request. Completion requires the Release and both managed
Windows directories to be physically absent.

Windows builders pass Gradle `-Dorg.gradle.daemon=false` so its JVM does not retain lint JARs
after a build. For an existing tree, Restart Manager identifies the lock owner. Only an IDLE
Gradle daemon holding a JAR inside that directory can be stopped: PID and creation time are
checked, and IDLE is rechecked before stopping. Active and unrelated processes are preserved;
deletion remains incomplete and can be retried.

Delete opens a mandatory version/build/full-SHA/package-count/scope dialog. Cancel and Escape do nothing.
Confirmation expires after five minutes and applies only to that project/SHA. The active builder stops and acceptance
owner data is restored before removing the exact local catalogue/checkout and matching GitHub Release.
The main source, Git tag and installed application remain.

A small tombstone is first written with read-back verification to this repository's `refs/notes/ai11-local-retention`.
Git notes create no branch and do not modify main history. Control commits contain the real task code and `[skip ci]`.
Network failure preserves packages and allows the same request to resume. Linux automatically fetches notes before jobs,
blocks the deleted SHA and reaps an unfinished attempt if necessary. It has no permanent archive, so Windows/GitHub deletion
never waits for Linux login/ack. The dashboard finishes deletion after persistent catalogues are cleaned.
Legacy retention drafts are migrated into notes and deleted after verification; new retention drafts are not created.

## Other projects

In that project's task, create its shared-engine profile, version helper, gates and gitignored
catalogue, then use `register-project` without a second server or package copies. For Linux add
an explicit `scripts/local_release/projects.json` entry: project, repository, directory, profile,
hosts and enabled. Arbitrary folders are never scanned. Each OS retains its own credentials.
Implement other projects' autobuilds in their corresponding tasks.

[OS exchange protocol](protocol.en.md) · [Release flow and gates](local-release.en.md).

Windows cleans the verified managed directory using extended-length paths, including deep Gradle files
and readonly Git files. A partial failure cannot produce an OS ack: local cleanup must physically finish.
Retry continues the original request; an already removed GitHub Release is not deleted again.
ADB starts in the permanent service directory to avoid holding a disposable checkout. Directory recovery can gracefully stop only the configured project ADB on its dedicated port after checking the SDK binary, PID, creation time and absence of devices. A shared lease protects active Android smoke tests. Global ADB5037 and unknown processes are preserved; Gradle recovery applies only to JAR files, never directories.
The confirmed version leaves the normal queue immediately to prevent automatic restoration.
Until cleanup finishes, the deletion section explicitly shows pending local removal or an error;
long error paths wrap inside the sidebar.

## Tooltips and Linux diagnostics

Control buttons explain their action on hover and keyboard focus; Escape hides the tooltip.
Descriptions reflect the OS, active process and completed gates. Restart stops then resumes checkpoints;
it does not request a full rebuild. After Windows completes, start/retry also sends Linux a resume request for its next login.
Stop while inactive also records and sends a log. Deletion retains its separate confirmation dialog.

The latest Linux report shows receipt time, last stage, available timing, error and log tail.
This diagnostic channel does not replace quality gates. Missing reports are explicitly shown as unavailable.
Progress is sent once per minute during Linux builds; completion, early failure and cleanup outcomes are sent separately.
Windows archives received history in `.local-releases/host-reports/`; full job logs stay in the canonical version catalogue.
Before final deletion of temporary transfer assets, every published job, including Windows-only jobs, saves a redacted `build-logs-<hash>.zip` to its GitHub Release. Download and SHA-256 are verified; archive failures preserve logs and transfer assets for retry. Linux can supplement the archive with its reports. Credentials and define values are removed before packaging.
Linux keeps no permanent archive - see the [temporary builder policy](local-release.en.md#linux-is-a-temporary-builder).

Controls hide equivalent actions: a new build shows Start, an attempted build shows Retry, and Restart appears only for an active process. Stop is hidden after the current OS completes. Recent Linux diagnostic history links open the saved Windows copies.

Windows Startup calls idempotent `start-service`, reusing a healthy server or starting a hidden server with `service.log`.
Before Windows serve/worker/run, a mandatory native gate checks a pythonw parent, 24 repeated Python/Git/cmd descendant cycles, console inheritance hidden at creation, and transient WinEvent show/foreground events. Unsafe creation flags are rejected before any child launch. CLI trees use python.exe and a private hidden console: pythonw or CREATE_NO_WINDOW on a parent alone is insufficient when a tool spawns ordinary descendants. Startup waits for the gate; replace stale idle observers only after active builders are released. The probe uses no screenshots or user input.
Concurrent queue writes wait up to five seconds without stealing a live lock.
Windows Context prepends its Python directory to child PATH and restores standard COM/EXE/BAT/CMD entries in child PATHEXT, including nested PowerShell scripts; the owner's system environment stays unchanged. Before ClearFix tool-tests, the profile attaches the isolated acceptance-report-tools cache, verifies versions against the pinned requirements-acceptance-reports.txt and installs missing tools there under a lock. If global pip is absent, it uses the official ensurepip bundled wheel without installing pip into the base interpreter. Missing pypdf never skips the suite; apply this environment repair to the existing job through an audited runtime update.
Linux keeps no archive, so deletion finishes after Windows/GitHub cleanup without a Linux login or receipt.
Small tombstones still block resurrection and reap an unfinished Linux outbox if necessary. Deletion markers persist in Git notes without a technical Release. Native Ubuntu runtime4/build174 passed Snap acceptance, verified delivery
and cleanup; Windows imported the result automatically.
