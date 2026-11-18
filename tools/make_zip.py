"""Build L2_colab.zip (code + notebooks + data/p1) with forward-slash paths, for upload to Colab or Kaggle.
Run from the repo root: python tools/make_zip.py"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"outputs", "__pycache__", ".ipynb_checkpoints", ".git", "recordings"}
SKIP_FILES = {"latest.ipynb", "ran.ipynb"}


def main(out="L2_colab.zip"):
    out_path = os.path.join(ROOT, out)
    n = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            at_root = os.path.abspath(dirpath) == ROOT
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                           and not (at_root and d.startswith("part"))]  # results folders are not needed to run
            for f in filenames:
                if f.endswith((".zip", ".pyc")) or f in SKIP_FILES or f.startswith("fin_run"):
                    continue
                if at_root and f.endswith(".ipynb"):  # loose downloaded notebooks in the repo root
                    continue
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                z.write(full, rel)
                n += 1
    print(f"wrote {out_path} ({n} files, {os.path.getsize(out_path) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
