"""Build the Canvas ZIP for Pair 44 deterministically (fixed timestamps, sorted entries, SHA256SUMS).

Contents (course requirement): the IEEE report PDF covering Parts 1-3, CONTRIBUTIONS.md, AI_USAGE.md, links.txt.
Nothing else (no notebooks, .git, weights, caches or secrets: those belong in GitHub / Hugging Face).

    python3 publication/build_canvas_zip.py            # PREVIEW zip if anything is still missing
    python3 publication/build_canvas_zip.py --final    # refuses unless every check passes

Run from the repository root inside the Lab 2 container. Output: $LAB2_WORK_DIR/submission/ (outside Git).
"""
import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = Path("/app/data266_lab2_work/submission") if Path("/app/data266_lab2_work").exists() else REPO.parent / "submission"
FINAL_NAME, PREVIEW_NAME = "Pair_Programming_Team_44.zip", "Pair_Programming_Team_44_PREVIEW.zip"
PDF = REPO / "report" / "data266_lab2_report.pdf"
FILES = {"CONTRIBUTIONS.md": REPO / "CONTRIBUTIONS.md", "AI_USAGE.md": REPO / "AI_USAGE.md", "links.txt": REPO / "links.txt"}
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def blockers():
    b = []
    if not PDF.exists() or not PDF.read_bytes()[:5] == b"%PDF-":
        b.append(f"report PDF missing: compile report/data266_lab2_report.tex and save it as {PDF.relative_to(REPO)}")
    tex = (REPO / "report" / "data266_lab2_report.tex").read_text(encoding="utf-8")
    n = len(re.findall(r"\\pending\{|\\missing\{", re.sub(r"(?<!\\)%.*", "", tex)))
    if n:
        b.append(f"report source still has {n} \\pending/\\missing markers")
    links = FILES["links.txt"].read_text(encoding="utf-8")
    m = [l.strip() for l in links.splitlines() if re.search(r"\b(MISSING|PENDING)\b", l)]
    if m:
        b.append(f"links.txt has {len(m)} MISSING/PENDING lines")
    contrib = FILES["CONTRIBUTIONS.md"].read_text(encoding="utf-8")
    if "TO BE FILLED" in contrib:
        b.append(f"CONTRIBUTIONS.md has {contrib.count('TO BE FILLED')} 'TO BE FILLED' fields")
    for name, p in FILES.items():
        t = p.read_text(encoding="utf-8")
        if re.search(r"hf_[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}", t):
            b.append(f"{name}: looks like it contains a token - remove it")
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    probs = blockers()
    if a.final and probs:
        print("REFUSED: not ready for the final Canvas ZIP:\n  - " + "\n  - ".join(probs))
        sys.exit(1)
    name = FINAL_NAME if not probs else PREVIEW_NAME
    stage = OUT_DIR / ("final" if not probs else "preview")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    entries = dict(FILES)
    if PDF.exists():
        entries[PDF.name] = PDF
    if probs:
        (stage / "PREVIEW_NOT_FOR_SUBMISSION.txt").write_text(
            "PREVIEW - NOT the Canvas submission. Open items:\n- " + "\n- ".join(probs) + "\n", encoding="utf-8")
        entries["PREVIEW_NOT_FOR_SUBMISSION.txt"] = stage / "PREVIEW_NOT_FOR_SUBMISSION.txt"
    for n, p in entries.items():
        if p.parent != stage:
            shutil.copyfile(p, stage / n)
    sums = "".join(f"{hashlib.sha256((stage / n).read_bytes()).hexdigest()}  {n}\n" for n in sorted(entries))
    (stage / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    zpath = OUT_DIR / name
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(entries) + ["SHA256SUMS.txt"]:
            info = zipfile.ZipInfo(n, FIXED_TIME)
            info.compress_type, info.external_attr = zipfile.ZIP_DEFLATED, 0o644 << 16
            z.writestr(info, (stage / n).read_bytes())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        listing = z.namelist()
    print(f"{'FINAL' if not probs else 'PREVIEW'}: {zpath} ({zpath.stat().st_size} bytes, sha256 "
          f"{hashlib.sha256(zpath.read_bytes()).hexdigest()[:16]})\n  contents: {listing}")
    if probs:
        print("  open items:\n   - " + "\n   - ".join(probs))


if __name__ == "__main__":
    main()
