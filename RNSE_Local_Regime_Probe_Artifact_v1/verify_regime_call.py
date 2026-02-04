#!/usr/bin/env python3
"""
verify_regime_call.py

IP-safe verifier for the RNSE Local Regime Probe proof artifact.

What it does:
1) Verifies SHA-256 digests for retained files.
2) Replays the *pre-declared regime call* on sweep_summary.json.

Exit code:
- 0 on PASS
- 1 on FAIL
"""

from __future__ import annotations
import argparse, json, os, sys, hashlib
from typing import Dict, Any, List, Tuple

DEFAULTS = {
    "eps_zero": 1e-4,
    "diffuse_max_abs_contrast": 5e-3,
    "ratio_min": 1.5,          # require bursty_contrast / kappa >= ratio_min for kappa>0
    "monotonic_tol": 1e-9,     # allow tiny float noise
}

REQUIRED_FILES = ["config.json", "sweep_summary.json", "digests.json"]

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_digests(artifact_dir: str, digests: Dict[str, str]) -> Tuple[bool, List[str]]:
    problems = []
    for rel, expected in digests.items():
        abs_path = os.path.join(artifact_dir, rel)
        if not os.path.exists(abs_path):
            problems.append(f"Missing file for digest: {rel}")
            continue
        got = sha256_file(abs_path)
        if got.lower() != expected.lower():
            problems.append(f"SHA mismatch for {rel}: expected {expected}, got {got}")
    return (len(problems) == 0), problems

def extract_contrasts(sweep: List[Dict[str, Any]]) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    bursty = []
    diffuse = []
    for row in sweep:
        k = float(row["kappa"])
        bursty_c = float(row["bursty"]["roi_probe"]["Delta_Lambda_roi_minus_bg"])
        diffuse_c = float(row["diffuse"]["roi_probe"]["Delta_Lambda_roi_minus_bg"])
        bursty.append((k, bursty_c))
        diffuse.append((k, diffuse_c))
    bursty.sort(key=lambda x: x[0])
    diffuse.sort(key=lambda x: x[0])
    return bursty, diffuse

def regime_call(bursty: List[Tuple[float, float]], diffuse: List[Tuple[float, float]], cfg: Dict[str, Any], thr: Dict[str, float]) -> Tuple[bool, List[str]]:
    issues = []

    # A) Null collapse at kappa=0
    k0_b = next((v for k, v in bursty if abs(k - 0.0) < 1e-12), None)
    k0_d = next((v for k, v in diffuse if abs(k - 0.0) < 1e-12), None)
    if k0_b is None or k0_d is None:
        issues.append("Missing kappa=0.0 row in sweep_summary.json")
    else:
        if abs(k0_b) > thr["eps_zero"]:
            issues.append(f"kappa=0 bursty contrast not ~0: {k0_b}")
        if abs(k0_d) > thr["eps_zero"]:
            issues.append(f"kappa=0 diffuse contrast not ~0: {k0_d}")

    # B) Diffuse must remain small
    for k, v in diffuse:
        if k > 0 and abs(v) > thr["diffuse_max_abs_contrast"]:
            issues.append(f"Diffuse contrast too large at k={k}: {v}")

    # C) Bursty separability + proportionality
    for k, v in bursty:
        if k <= 0:
            continue
        if v <= 0:
            issues.append(f"Bursty contrast not positive at k={k}: {v}")
        ratio = v / k
        if ratio < thr["ratio_min"]:
            issues.append(f"Bursty contrast/kappa ratio too small at k={k}: {ratio} (<{thr['ratio_min']})")

    # D) Monotonic non-decreasing bursty contrast w.r.t kappa
    prev = None
    for k, v in bursty:
        if prev is not None and v + thr["monotonic_tol"] < prev:
            issues.append(f"Bursty contrast not monotonic: k={k} v={v} < prev={prev}")
        prev = v

    return (len(issues) == 0), issues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact_dir", default="proof_artifact", help="Directory containing retained artifact files")
    ap.add_argument("--thresholds", default=None, help="Optional JSON file overriding thresholds")
    args = ap.parse_args()

    artifact_dir = args.artifact_dir

    # Load required
    for fn in REQUIRED_FILES:
        if not os.path.exists(os.path.join(artifact_dir, fn)):
            print(f"FAIL: missing required file: {fn}", file=sys.stderr)
            return 1

    cfg = load_json(os.path.join(artifact_dir, "config.json"))
    sweep = load_json(os.path.join(artifact_dir, "sweep_summary.json"))
    dig = load_json(os.path.join(artifact_dir, "digests.json"))

    thr = dict(DEFAULTS)
    if args.thresholds:
        thr.update(load_json(args.thresholds))

    ok_dig, dig_issues = verify_digests(artifact_dir, dig.get("sha256", dig))
    if not ok_dig:
        print("FAIL: digest verification failed")
        for x in dig_issues:
            print(" -", x)
        return 1

    bursty, diffuse = extract_contrasts(sweep)
    ok_regime, regime_issues = regime_call(bursty, diffuse, cfg, thr)
    if not ok_regime:
        print("FAIL: regime call failed")
        for x in regime_issues:
            print(" -", x)
        return 1

    print("PASS")
    print("\nRegime call summary (bursty ROI-vs-bg contrast):")
    for k, v in bursty:
        print(f"  k={k:0.3f}  contrast={v:0.6f}")

    print("\nDiffuse ROI-vs-bg contrast (should stay ~0):")
    for k, v in diffuse:
        print(f"  k={k:0.3f}  contrast={v:0.6f}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
