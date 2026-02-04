# Minimum Sufficient Evidence Checklist (v1)

This checklist defines what must be retained so a third party can **replay the regime call** without engine internals.

## A. Must be fixed (required for a valid replay)

1. **Decision rule**
   - The rule used to declare the regime call (thresholds, monotonicity checks, etc.)
   - Versioned (commit hash / digest)

2. **Run specification**
   - Seed(s) / seed64
   - Tick count / sampling cadence
   - Grid geometry (width/height)
   - Injection patterns (e.g., “bursty_center”, “diffuse”) and any fixed parameters of those patterns
   - ROI definition (shape + location) and background mask definition

3. **Retained outputs**
   - `sweep_summary.json` for the kappa sweep
   - `maps.npz` (map-level fields + ROI/background masks) for at least one representative run
   - `config.json`
   - `digests.json` covering the retained files

4. **Digesting**
   - SHA-256 over each retained file
   - (Optional) a manifest digest over a canonicalized manifest

## B. May vary (does NOT invalidate the replay)

- CPU/GPU model
- OS
- File paths / folder names
- Runtime and logging verbosity
- Python micro-version, *as long as you are only replaying the regime call on retained outputs* (no regeneration)

## C. Invalidates the replay (must be treated as a new surface)

- Any change to:
  - ROI definition or background mask definition
  - map aggregation (mean vs median; abs vs signed; clipping)
  - probe definition (what is “Lambda”, what is “chi”, which pixels are included)
  - thresholds / monotonicity criteria in the decision rule
  - permutation/null model definition (if included)
- Any missing retained file or SHA mismatch in `digests.json`

## D. Recommended “proof set” for public review

Minimum:
- `config.json`
- `sweep_summary.json`
- `digests.json`
- `verify_regime_call.py`

Nice-to-have:
- `maps.npz`
- `summary.json`
- a short plot (optional) generated from the sweep for readability
