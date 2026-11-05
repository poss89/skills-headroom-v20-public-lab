# SKILLS V21 — Headroom 0.42.0 isolated pilot proposal (NOT AUTHORIZED TO RUN)

Checkpoint: 2026-11-05. Owner requested **preparation and upload**, not execution. This PR is a staging/review artifact; **do not merge or dispatch without a subsequent explicit Owner decision**.

## Verified inherited boundary

- V20 public-lab run #2: scoped PASS for Docker daemon, `--network none`, non-root, read-only filesystem, capability drop, no host mounts, CPU 1, memory 2 GiB, PIDs 128. It is not a full security certification.
- V19 Replit: `BLOCKED_ISOLATION`; no candidate was run.
- V18: `ATTESTATION_PRESENT_UNVERIFIED`, `BINARY_SOURCE_EQUIVALENCE=NOT_PROVEN`, `TRANSITIVE_LICENSE_CLOSURE=OPEN`.
- V14–V18 are not to be repeated; no IDE, MCP, UAM, AnyContent, or production changes.

## Contents of this proposal

1. `.github/workflows/v21-headroom-pilot.yml` — a **manual-only documentary preflight**: fetches official public PyPI JSON metadata for Linux x86-64 wheel candidates and declared requirements. Does **not** download wheel bytes or install/run Headroom.
2. `v21/v21_synthetic_runner.py` — an **unexecuted**, synthetic-data-only harness, pinned to `headroom-ai==0.42.0`. Its use must await a further approved, OS-isolated runtime workflow. The harness uses Headroom's own round-trip verification and does not constitute an independent correctness or security proof.

## Mandatory gate before any Headroom execution

A future proposal must explicitly define and seek approval for:
- Selected Linux wheel, actual SHA256 computed from downloaded bytes, associated metadata/provenance evidence, and all resolved transitive wheel dependency SHA256/versions/license inventory.
- Base OCI image by immutable digest; dependency acquisition separated from runtime; binary-only packages and `--no-index` installation; verify all wheel digests. Any package build/install must not run in an untrusted host workspace and must be separately scoped/isolated.
- Offline runtime (Docker `--network none`), non-root, read-only rootfs, no mounts/secrets, drop capabilities, no-new-privileges, seccomp/AppArmor, 1 CPU, <=2 GiB RAM, <=128 PIDs, <=180 s and explicit cleanup. No ML model downloads, proxy, CCR, Kompress, OpenAI API calls, telemetry egress or real transcripts.
- Measured timing, peak RSS/cgroup RAM, token before/after with unchanged tokenizer, repeated output and internal reverse checks; zero-count fallback does not count as compression. A separate independently implemented semantic/structural preservation check is still needed.
- Stop-on-fail; no automatic retry or host rollout. V21 metadata preflight success is NOT candidate test authorization.

## Governance

`OWNER_APPROVAL_FOR_V21_RUNTIME=NOT_GRANTED`

`HEADROOM_FUNCTIONAL_RUNTIME=NOT_TESTED`

`SECURITY_PASS=NOT_GRANTED`

`G1_COMPLETE=OPEN`

`G3_DESKTOP=NOT_MEASURED`

`G4_DESKTOP=NOT_TESTED`

`SKILLS_MACROPHASE=45% PROVISIONAL_UNCHANGED`

Public repository is temporary; never store private material here. Preserve evidence in an authorized private destination before switching repository private, by Owner action.
