Appendix: Replay Spine Checklist v1.1
Minimal requirements for surface-only replay and audit of an RNSE regime call.
This checklist defines the public, portable replay spine required for third-party verification without access to engine internals.
RNSE is treated as a testbed, not a dependency.
Engine internals are explicitly out of scope.
Scope
Applies to replay of:
map-level diagnostics
regime calls
audit-relevant decisions
Assumes:
black-box engine
surface-only evidence
byte-stable verification across stacks
Requirements
A replay bundle claiming compliance MUST satisfy all items below.
1. Deterministic Canonicalization
All objects used for hashing MUST be canonicalized deterministically.
Required:
Encoding: UTF-8
Line endings: LF (\n) only
Trailing newline: REQUIRED
Object keys: lexicographically sorted
No BOM
No trailing whitespace
Optional or implementation-dependent behavior is not permitted.
2. Per-Artifact Hashing
Each surface artifact MUST have:
SHA-256 digest
computed over raw file bytes
encoded as lowercase hex
Typical artifacts include:
config
seeds
map-level outputs
diagnostic summaries
rule definitions / outputs
3. Bundle Digest (Surface Object)
A bundle-level digest MUST be provided.
Algorithm: SHA-256
Digest input (canonicalized):
mse_version
declared artifact list (paths + per-artifact digests)
Explicitly excluded:
timestamps
human-readable identifiers
freeform metadata (bundle_id, comments, notes)
This allows metadata to vary without breaking replay.
4. Rule Output (MUST when Audit-Relevant)
If a diagnostic rule produces an audit-relevant output, that output:
MUST be included as a surface artifact
MUST be hashed like any other artifact
MUST NOT be regenerated implicitly during replay
Categorization (maps vs digests) is repo-convention dependent; inclusion in the hashed surface is mandatory.
5. Replay Validity
A replay is VALID iff:
all declared artifacts exist
all per-artifact hashes match
the bundle digest matches
canonicalization rules are satisfied exactly
Any mismatch INVALIDATES the replay.
Non-Goals
This checklist does NOT:
specify engine internals
require engine determinism
constrain update rules or architectures
define optimization or termination behavior
It locks evidence, not implementation.
Summary
This appendix defines a portable replay spine that is:
surface-only
byte-stable
audit-friendly
implementation-agnostic
Designed for disciplined verification under partial observability.
