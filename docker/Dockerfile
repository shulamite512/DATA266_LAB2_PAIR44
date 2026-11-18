# DATA 266 Lab 2 — Parts 2 and 3 GPU environment (DECISIONS.md D-089).
# Base: official PyTorch runtime image. torch 2.14.1 + CUDA 13.0 wheels include sm_120 (RTX 5090) and sm_75 (T4).
# torch / torchvision / torchaudio / triton / nvidia-* wheels from the base image are PROTECTED by a constraints
# file: pip may not upgrade, downgrade or replace them. The build fails if torch changes.
FROM pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PYTHONUNBUFFERED=1

# git: required by the run-information cell (git rev-parse) and for recording the working-tree state.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*'

COPY requirements-p2p3.in /opt/lab2/requirements-p2p3.in

RUN set -eux; \
    cd /opt/lab2; \
    pip list --format=freeze | grep -iE '^(torch|torchvision|torchaudio|triton|nvidia-[a-z0-9-]+)==' > constraints-base.txt; \
    echo 'regex<2026.11' >> constraints-base.txt; \
    python -c "import torch; open('torch_version_before.txt','w').write(torch.__version__)"; \
    pip install --dry-run -r requirements-p2p3.in -c constraints-base.txt > dryrun.txt 2>&1 || { tail -40 dryrun.txt; exit 1; }; \
    pip install -r requirements-p2p3.in -c constraints-base.txt; \
    python -c "import torch; b=open('torch_version_before.txt').read(); assert torch.__version__ == b, (b, torch.__version__)"; \
    (pip check > pip_check.txt 2>&1 || true); \
    pip list --format=freeze > requirements-p2p3.lock.txt

WORKDIR /app/implementation
EXPOSE 8888 7860

# The token comes from JUPYTER_TOKEN (docker/.env). Ports are published to 127.0.0.1 only (compose.yaml).
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", \
     "--ServerApp.root_dir=/app", "--ServerApp.allow_remote_access=True"]
