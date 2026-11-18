"""Install the pinned requirements, skipping packages preinstalled on Kaggle/Colab.

Usage (from the repo root):  python -m src.common.install
Installs everything in one pip call; if that fails, installs package by package and, for a
package whose pinned version has no wheel for this Python, falls back to the latest version
and prints a WARNING so requirements.txt can be updated to the version actually used.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _pip(args):
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *args], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr)[-2500:]


def main(path=os.path.join(ROOT, "requirements.txt")):
    keep = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#") or "# preinstalled" in s:
                continue
            keep.append(s.split("#")[0].strip())
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
        tmp.write("\n".join(keep))
    ok, log = _pip(["-r", tmp.name])
    if ok:
        print("installed (pinned):", ", ".join(keep))
        return 0
    print("bulk install failed, retrying one by one. pip said:\n", log)
    failed = []
    for req in keep:
        ok, log = _pip([req])
        if ok:
            continue
        name = req.split("==")[0]
        ok2, log2 = _pip([name])
        if ok2:
            print(f"WARNING: {req} unavailable for Python {sys.version.split()[0]}; installed latest {name}. "
                  f"Update requirements.txt to the version printed by Cell 1.")
        else:
            failed.append(req)
            print(f"FAILED: {req}\n{log2}")
    if failed:
        print("could not install:", failed)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
