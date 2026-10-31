# Local Revelation releases

Doc-Version: 1.0.1
Last-Updated: 2026-10-31
Source-Commit: working-tree

[Shared build dashboard and startup](build-service.en.md) - http://127.0.0.1:8877.

REV301 is still implementing the migration. The hosted workflow stays until a complete real trial,
GitHub asset read-back and trigger verification pass. Stores, the production website and Supabase deployment
remain separate version tasks after acceptance.

Child [REV302](https://ai11.link/cabinet/tasks?project=1&task=REV302) implements one shared local service for all projects:
versions/platforms/packages, current stages and queue, start/retry/stop, automatic startup and a fixed local URL.
The service reads the same package files. Other projects' autobuilds are implemented in their own tasks
and connected through this coordinator's profiles/queues/catalogues. The Windows service is installed;
the next real login and Linux startup are separate host checks, and the REV301 rollout remains incomplete.

## Primary local catalogue

Use `.local-releases/releases/revelation/<version>+<build>/<full-Git-SHA>/`.
Its `packages/` directory holds each APK, AAB, EXE, MSIX, Web ZIP, Linux TAR.GZ and Snap exactly once.
The same release directory contains `job.json`, `manifest.json`, `source.bundle`, its pinned `runtime/`,
`results/`, `logs/<os>/<step>.log` and `publication.json`. Deployment reads these package files directly.
There is no separate `jobs` directory or duplicate package archive.

Everything in `.local-releases/` is Git-ignored. Short-lived isolated builder checkouts use `w/<short-SHA>/<os-initial>/`.
They are working files, not a second release archive. `github-index.json` indexes restored historical releases.
The current migration report is `.local-releases/REV301-report.md`.
The manifest records relative package paths, sizes, SHA-256 and status: `incomplete` is not ready;
`archived` means a historical release was downloaded, without claiming its tests ran again.
Never substitute another version/SHA or silently overwrite a conflicting package.

## Windows commands

Prerequisites: Python 3.10+, Git, Flutter 3.47.2, Java 17, Android SDK, Visual Studio C++/Windows SDK and Inno Setup.
Host configuration points to `defines_file`, `sentry_properties`, `inno_setup`, and optionally `environment`,
`android_sdk`, `android_device`, `chromedriver_port` and `web_port`.
Before Android commands the coordinator checks generated Flutter plugin paths and, when needed, regenerates them
with `flutter pub get` from the physical checkout. Temporary SUBST paths are reserved for Windows/MSBuild;
Android must not depend on a drive letter removed after the run. `android-cache-recovery` validates
`gradlew help --offline`, preserving existing packages and the failed attempt in its recovery evidence.
Existing `SIGNING_*` environment variables
provide Android signing. Keep credentials outside Git, jobs, AI11 and handoff payloads.
Set the working keystore through host-local `signing_store_file`; the builder verifies its private-key password
and `expected_signing_certificate_sha256`. Key/password values never enter the portable job.
Production builds set `SENTRY_ENVIRONMENT=production` without changing the developer's original config.

```powershell
python scripts/local_release/release.py prepare --repo . --profile scripts/local_release/revelation.json --root .local-releases --config .local-releases/windows-config.json
python scripts/local_release/release.py run --job <canonical-directory> --config .local-releases/windows-config.json --phase quality
python scripts/local_release/release.py run --job <canonical-directory> --config .local-releases/windows-config.json --phase integration
python scripts/local_release/release.py run --job <canonical-directory> --config .local-releases/windows-config.json --phase build
python scripts/local_release/release.py send-result --job <canonical-directory> --config .local-releases/windows-config.json
python scripts/local_release/release.py handoff --job <canonical-directory> --config .local-releases/windows-config.json
```

Omit `--phase` to run all host stages. Flutter commands are sequential. Preserve all legacy quality checks,
including separate unit/widget runs, coverage, LCOV filtering and the 90% effective threshold.
Local integration, docs sync and package/signature checks are additional gates. Preserve device data/settings;
an unavailable device is not a passing result. Use the existing version helper before selecting the source SHA.
Never increment version/build inside an already prepared job.

## Isolated Linux and transport

Linux does not need a Windows disk or live Windows session. After the approved tooling commit/push is available,
update the Linux checkout and run:

```bash
bash scripts/local_release/run-linux.sh
```

The entrypoint receives its job from the owned draft GitHub Release, verifies the source/runtime hashes,
uses its own isolated checkout and saves results in its own canonical local catalogue.
The default host config is `~/.config/ai11-local-release/revelation.json`.
Each OS needs independent GitHub authentication (`GH_TOKEN`, protected token file, native Git credential helper or `gh auth`)
and its own local Sentry token. Windows secrets are not transferred. Flutter/native/Snap tools must actually be available on Linux.
Automated Snap executes the entire original `snapcraft_build.sh` from the pinned source SHA in an isolated input checkout:
`rm -rf build`, `flutter clean`, `flutter pub get`, `flutter run -d linux --debug --dart-define-from-file=api-keys.json`,
`snapcraft clean`, `snapcraft pack`, and `Build complete`. Its Git blob is verified before execution;
commands and order are never shortened. The job's release override-build and pinned Flutter SDK remain.
Only `q` input is automated through a real Linux PTY after Flutter's command banner, application startup and five seconds alive.
That debug process uses isolated XDG Documents/config/data/cache. Snapcraft retains the original environment.
Full-script execution evidence is saved as `results/linux-snap-script.json`. Manual `./snapcraft_build.sh`
retains its original behavior; automated multi-project dispatch uses `run-linux.sh`.
Built-in `verify-linux` installs the exact SHA-256 inspected package, requires actual Flutter startup and ten seconds
alive, then restores the original Snap revision, tracking and data snapshot. The owner's Snap data directory is temporarily
renamed beside its original location; the exact files are returned and checked by a combined digest, including caches
excluded from snapshots. If no app was installed, only the matching temporary installation is removed.
Smoke uses isolated XDG config/data/cache/Documents inside Snap instead of owner data.
Restoration runs even after failure or cancellation. Its host-local recovery journal is
`.local-releases/w/<short-SHA>/snap-acceptance/restore.json`; after interruption the next run restores first.
Data snapshots are never sent to GitHub. Installation uses `sudo -n snap`. If authentication is needed,
the graphical progress terminal asks once through `sudo -v`; passwords are neither stored nor logged.
No persistent passwordless/sudoers permission is created. Without an interactive terminal or available sudo,
acceptance remains incomplete with a concrete instruction. An explicitly pinned custom verifier remains supported
through `snap_verify_script` and `snap_verify_script_sha256`. Failed acceptance preserves the draft;
package transfer remains independent. Bounded safe history candidates are collected as evidence; shell history is not executed automatically.

Linux uploads verified packages and current status, including redacted logs after a failure. It preserves a nonzero exit code.
If network/authentication prevents upload, the result remains in the local outbox for retry; remote delivery is not claimed.
After returning to Windows:

```powershell
python scripts/local_release/release.py sync --job <canonical-directory> --config .local-releases/windows-config.json --cleanup
```

Sync verifies the run identity and hashes, durably stores packages/evidence/logs, then deletes only known temporary exchange IDs.
Package assets, `SHA256SUMS` and the final release manifest remain as the external backup.
A public GitHub Release requires all seven packages and both hosts' gates. A successful Linux stage alone is insufficient.

## Archive, queue and recovery

```powershell
python scripts/local_release/release.py archive --profile scripts/local_release/revelation.json --root .local-releases --config .local-releases/windows-config.json
python scripts/local_release/release.py verify-packages <canonical-directory>
python scripts/local_release/release.py status --job <canonical-directory>
python -m unittest discover -s tools/local_release/tests -v
python scripts/local_release/inventory.py --check
```

Archive follows every releases/assets page, verifies size and any publisher SHA-256, computes a local SHA-256,
and records original URLs/IDs plus the resolved tag SHA. Historical versions are downloaded, not rebuilt.
Existing files are checked instead of downloaded again without reason.

The shared engine is `tools/local_release/`; Revelation's profile is `scripts/local_release/revelation.json`.
The [53-step parity inventory](../../../scripts/local_release/workflow-inventory.json) pins the original workflow Git blob.
Other projects should supply profiles to this engine instead of forking coordinators.

`init-queue` records a historical boundary without activation. `install-trigger` requires a complete published real trial.
Until then, production hooks/startup workers stay inactive; hook tests use private repositories.
`[skip ci]` anywhere in the full message skips automatic build-number increment and build/publication.
Every other new local/received-remote SHA gets its own durable entry without branch/path/author filters or latest-only replacement.
Existing hooks are chained and restored on removal. Different SHAs with the same version/build retain separate local packages;
an external tag collision blocks publication and never changes the source or overwrites a release.
Use `retry --queue <queue-file> --sha <full-SHA>` to retry one failed/waiting job.
OS-backed locks release after process exit/crash; a live builder is never displaced by a timeout.

The coordinator enumerates every `integration_test/**/*_test.dart`, including smoke, and runs each file
in a separate Flutter process with its own checkpoint. With Flutter 3.47.2 this also avoids
`DesktopLogReader` closing after the first desktop application. Retry retains passed files and runs the remainder;
the aggregate integration gate passes only after the complete suite.

The [Windows/Linux protocol](protocol.en.md) defines jobs, runtime repairs, partial packages, logs and receipts. Implementation uses main; exchange needs no separate branch.
