Minimum Sufficient Evidence (MSE) for replay  - RNSE - Elad Genish

The rule output is treated as a first-class audit artifact under the MSE replay contract.

This repository is a **minimal, IP-safe “proof artifact”** for a *regime call* on RNSE-style diagnostics:

- the **engine runs** (internals not included here)
- the **diagnostic decides** using a **pre-declared, map-level / local probe rule**
- a third party can **replay the regime call** using only retained outputs + a small verifier script

The goal is *not* to reproduce RNSE internals. The goal is to make the **measurement surface** auditable.

## What’s included

`proof_artifact/`
- `config.json` — run parameters (seed(s), ticks, grid geometry, ROI definition, probe cadence)
- `sweep_summary.json` — kappa sweep results for **bursty** vs **diffuse** injection patterns
- `summary.json` — single-run summary (if present for the run that produced `maps.npz`)
- `maps.npz` — map-level outputs (e.g., Lambda map, chi map, ROI/background masks)
- `digests.json` — SHA-256 digests for the retained files

Top-level:
- `verify_regime_call.py` — replays the **decision rule** + verifies SHA-256 digests
- `MINIMUM_EVIDENCE_CHECKLIST.md` — what must be fixed / can vary / invalidates a replay

## Quick start

```bash
python verify_regime_call.py --artifact_dir proof_artifact
```

If everything is consistent, the script prints **PASS** and a short report of the regime call.

## The pre-declared regime call (human description)

1. **Null collapse:** at κ = 0, the local contrast should collapse (≈ 0) for both patterns.
2. **Local separability:** for κ > 0, the **bursty ROI-vs-background Λ contrast** should be:
   - strictly positive
   - roughly proportional to κ
   - much larger than the diffuse ROI-vs-background contrast
3. **Monotonicity:** bursty contrast should be non-decreasing as κ increases.

That’s the externally checkable “two regimes” envelope:
- κ = 0 → collapse
- κ > 0 → separation visible under local probes

(Exact thresholds are in `verify_regime_call.py` and are part of the retained surface.)

## Notes

- “Regime” here refers to **observer sensitivity / measurement validity**, not any halt, convergence, or acceptance of the underlying engine.
- If you want to regenerate the outputs, you can do so with your own engine runner, but this package is designed so reviewers do **not** need engine internals to verify the *decision*.
