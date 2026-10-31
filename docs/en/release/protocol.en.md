# Local builder exchange

Doc-Version: 2.0.10
Last-Updated: 2026-10-31
Source-Commit: working-tree

Git main stores tools, profiles and the [project catalogue](../../../scripts/local_release/projects.json).
Owned draft GitHub Releases carry jobs, packages, results and redacted logs. Credentials and binaries stay outside Git.
Each other project registers its profile in its own task; Revelation is currently the only enabled project.

## Deletion and prevention of reimport

A separate unpublished control draft `ai11-local-retention-<project>` has the marker
`<!-- local-release-retention:<project>:1 -->`. It is excluded from package archives and final releases.
`delete-<request_id>.json` contains schema1, project/repository, version/build/SHA, exact release ID/tag
and expected OS roles, without paths, commands or secrets. UI confirmation saves one request under
`.local-releases/deletions/<project>/<SHA>.json`, then sends it with download/hash read-back.

Tag SHA and release ID are verified before deleting the GitHub Release. The coordinator constructs local
paths. An active process stops and owner data is restored before checkout cleanup. Recursive removal
is restricted to exact managed paths; foreign snapshots/SHAs and pending recovery journals are protected.
After cleanup each OS sends immutable `ack-<request_id>-<os>.json`. Requests/acks require the repository
owner's GitHub uploader identity (another verified actor can be set in host-local `retention_actor`).

Linux processes control records before job discovery/intake. The permanent tombstone blocks prepare/run,
queue retry, handoff/publication, receive and archive for the deleted SHA. Network failures retain durable
pending state; retry uses the same request ID. The GitHub Release is removed entirely and its Git tag remains.
Receipts let Windows distinguish completed local cleanup from a pending Linux login.

## Stage time

Result schema1 accepts stage `duration_seconds`, cumulative `total_duration_seconds`, `attempts`,
`parent_step`, `timing_exact` and `timing_partial`. Host-local `monotonic_started` is read only for
a live builder on the current OS with a matching session_id. Completed durations transfer between OSs;
another host's monotonic counter is never compared with ours. `timing_totals` retains spent time when
a checkpoint is invalidated. Totals include only root stages; nested stages remain available as detail.
Legacy data is explicitly estimated, and missing/reversed measurements are not invented as zero.
Waiting between separate runs is excluded.

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

`attempt_runtime_revision` identifies the revision actually executed; `pending_runtime_revision` identifies
a delivered repair awaiting its next attempt. Windows can show repair readiness separately from the old error.
`refresh-runtime --reason <description>` records the repair reason in the job history.
For an audited acceptance-only change, add `--invalidate-step linux:verify-linux`. The explicit checkpoint list
is recorded in both the job audit and envelope; reception checks their agreement and transitively invalidates dependents.
All original gates remain mandatory. Changed source overlays prohibit preserving old build checkpoints this way.
The default remains full Linux recipe invalidation. Runtime15 uses `--invalidate-step linux:snap`: it repeats
the entire original Snap script and inspection/install/smoke once, preserving the built TAR and passed integration tests.
The superseded private Snap remains one local file; the manifest marks it pending and preserves its verified
previous draft asset ID. A collision without an attested remote backup still prevents replacement.
Runtime16 preserves these checkpoints and fixes sudo TTY handling and temporary authentication for installed Snap acceptance.
Runtime17 repeats only `verify-linux`: protected Snap checksums use authenticated sudo, preserving the successfully
built Snap16, TAR, and every passed build/test checkpoint.
Runtime18 also repeats only `verify-linux`: runtime17 installed the package successfully, but the owner closed
the test window before the ten-second observation finished. Clear instructions, a countdown, one launch-only
retry after a normal early close, and exit/startup/timing evidence are now included.
The required ten seconds, built packages and passed build/test checkpoints are preserved.

Snap-only tools are checked in Snap stages, preserving portable TAR independence.
In squashfs-tools 4.6.1, `unsquashfs -version` prints its version and exits 1 without an input image.
Only this diagnostic accepts that code with a recognizable version banner. Actual package-content checks
still require code0. See the [4.6.1 source](https://github.com/plougher/squashfs-tools/blob/4.6.1/squashfs-tools/unsquashfs.c).

Receipts acknowledge exact asset IDs/digests. Base jobs/runtime repairs remain until complete success for recovery.
Cleanup removes only owned acknowledged temporary IDs; temporary package assets require a verified public mirror.
Canonical packages, checksums and final manifest remain.
After full success Windows verifies all gates, local source/runtime/package hashes and public package/checksum/manifest
assets, then persists `results/exchange-closed.json` before the first deletion. This final receipt closes the completed
exchange, including old runtime revisions and intermediate status/log/package assets under this exact run's prefix.
Only recognized names and recorded IDs are removed; other runs and unknown files remain. Cleanup can safely resume
without another Linux login. The local catalogue then links to normal public assets rather than deleted transport copies.
Repeated handoff checks the existing base asset before compressing source.bundle again.
A saved receipt with the exact identity/asset ID/hash plus a fresh GitHub digest reuses an unchanged base
or package without downloading the large file again. The first upload still requires complete download
read-back; a missing receipt, new ID or changed digest requires verification again.
On the next Linux login a completed release is recognized through its public final manifest: source/tag/build/defines,
the complete required gate list, every package's metadata and SHA256SUMS are verified.
A local `publication-received.json` records the acknowledgment without fabricating old local checkpoints.
The release is skipped without building or recreating removed transport files. After publication the dashboard
can confirm another OS through that manifest while preserving its earlier local attempt history.
New source snapshots containing the inventory script require `workflow-parity` on Windows and Linux.
Inventory records whether the hosted YAML exists; after cutover the guard rejects its reintroduction,
while preserving parity for the original3jobs/53steps from its immutable Git blob. Historical snapshots
without that script gain no impossible gate and retain their successful checks.

## Numbering and login

A new local commit without `[skip ci]` increments build once through the project helper and synchronizes four version files.
Git caches the tree before commit-msg, so a guarded internal amend with hooks disabled completes one visible commit.
Discovery observes the finalized SHA. Signing retries never increment twice. `[skip ci]` in title/body skips numbering and dispatch;
receiving existing remote commits never renumbers them.

Initial Ubuntu setup: update main and run `bash scripts/local_release/run-linux.sh`.
It registers the profile and installs user XDG autostart without root. Later graphical logins open a progress/summary terminal
for all registered projects. A missing exact Flutter SDK is provisioned in user cache, preserving the global SDK.
Snapcraft executes the entire original `snapcraft_build.sh`, including its preliminary debug run;
only its `q` input is automated through an isolated PTY. Release override-build remains unchanged.

The new graphical-login cycle and Snap install/smoke must be verified in Ubuntu; unavailable execution is not PASS.
