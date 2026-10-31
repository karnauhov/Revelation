# Local builder exchange

Doc-Version: 2.0.0
Last-Updated: 2026-10-31
Source-Commit: working-tree

Git main stores tools, profiles and the [project catalogue](../../../scripts/local_release/projects.json).
Owned draft GitHub Releases carry jobs, packages, results and redacted logs. Credentials and binaries stay outside Git.
Each other project registers its profile in its own task; Revelation is currently the only enabled project.

## Job identity

`run_id = <project>-<full-source-SHA>` and tag `v<version>+<build>`. `job.json` records source SHA,
version/build, profile, architectures, expected package names, source.bundle SHA-256, production defines digest
and every pinned Python runtime file hash. Each OS retains its own credentials and paths.

JSON envelopes retain `schema: 1`, with separate `protocol_version: 2`. Version 1 results remain readable;
unknown newer protocol versions are rejected.

## Paths and roles

Each OS uses `.local-releases/releases/<project>/<version>+<build>/<SHA>/` with one `packages/`,
job.json, manifest.json, source.bundle, runtime, results and `logs/<host>/`. The shared service indexes these files directly.

| Data | Location |
|---|---|
| Credential-free project list | `scripts/local_release/projects.json` in coordinator main |
| Host repository/profile paths | `%LOCALAPPDATA%/AI11/LocalRelease/registry.json` or `~/.config/ai11-local-release/registry.json` |
| Windows settings/credentials | `.local-releases/windows-config.json`, machine environment and protected keystore |
| Linux settings/credentials | `~/.config/ai11-local-release/<project>.json` and private Linux checkout files |
| Current stage/checkpoints | `results/<host>.json` |
| Receive receipts | `results/<host>-received.json`, received.json and runtime receipts |
| Pending transmission | `results/<host>-outbox.json` |
| Linux repair plan | `results/linux-remediation.json`, `results/linux-repair.sh` |

Windows prepares sources and receives Linux results. After graphical login, Linux updates main, reads the catalogue
and sequentially processes registered Linux profiles. Each new eligible commit gets its own job; `[skip ci]` is skipped.
Either side can finalize a release when all verified peer results are available.

## Owned draft assets

Prefix: `local-transfer-<run_id>-`. Ownership requires the `<!-- local-release:<run_id> -->` marker,
source SHA and matching tag. Foreign drafts are preserved.

| Suffix | Content |
|---|---|
| `job.tar.gz` | Original immutable job, source.bundle, runtime and notes |
| `runtime-v<N>.tar.gz` | Audited coordinator/job revision without retransmitting source.bundle |
| `<host>-status.json` | Identity, runtime revision, checkpoints, package IDs/digests, evidence and receipts |
| `<host>-logs.zip` | Redacted per-stage logs for this OS |
| `<host>-package-<SHA256>-<canonical-name>` | Immutable temporary package identified by its content |

Download validates size/SHA-256; bundle and runtime hashes are checked before execution.
Already received bundles are reused. Archive paths must stay inside the receiver; symlinks, directories and oversized runtime updates are rejected.

## Partial success

Each produced file can be sent independently. `built_unverified` retains a diagnostic package;
`structure_verified` indicates its inspection gates passed. Neither means the complete release passed.
Hash-qualified temporary names prevent silent replacement during repair. `manifest.json` tracks diagnostic files
under `unverified_packages`, with one canonical local copy.

Missing Windows packages never block Linux. Snap failure does not prevent TAR.GZ, or vice versa.
Network failure preserves local packages/outbox. Quality, integration, Sentry and install/smoke failures remain
visible and continue blocking public finalization even when private draft binaries are available.

Finalization requires every mandatory gate on both hosts, equal compile inputs and the complete artifact set.
Only then are canonical package names, SHA256SUMS and release-manifest.json published.
Published historical releases remain immutable and are downloaded instead of rebuilt.

## Repair and acknowledgment

Windows publishes an audited runtime update with increasing revision, predecessor/new job digests and tooling Git SHA.
Reception preserves source SHA/build/version/architectures and rejects removal of mandatory gates.
Runtime replacement is atomic and waits for builder locks; packages and verified checkpoints remain.
Linux CMake/Snap packaging corrections use exact `generated_source_overlays` digests rather than arbitrary source edits.
Published jobs cannot be repaired in place.

Linux receives the repair before execution, runs known diagnostic commands and retries necessary stages.
Error text and shell history are data, never commands to evaluate. Unknown failures return fresh logs.

Receipts acknowledge exact asset IDs/digests. Base jobs/runtime repairs remain until complete success for recovery.
Cleanup removes only owned acknowledged temporary IDs; temporary package assets require a verified public mirror.
Canonical packages, checksums and final manifest remain.

## Numbering and login

A new local commit without `[skip ci]` increments build once through the project helper and synchronizes four version files.
Git caches the tree before commit-msg, so a guarded internal amend with hooks disabled completes one visible commit.
Discovery observes the finalized SHA. Signing retries never increment twice. `[skip ci]` in title/body skips numbering and dispatch;
receiving existing remote commits never renumbers them.

Initial Ubuntu setup: update main and run `bash scripts/local_release/run-linux.sh`.
It registers the profile and installs user XDG autostart without root. Later graphical logins open a progress/summary terminal
for all registered projects. A missing exact Flutter SDK is provisioned in user cache, preserving the global SDK.
Snapcraft retains the confirmed clean/pack sequence and release override-build, without interactive flutter run.

The new graphical-login cycle and Snap install/smoke must be verified in Ubuntu; unavailable execution is not PASS.
