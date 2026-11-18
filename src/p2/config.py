"""Part 2 settings. Both runs share data, step budget, batch size and learning rate;
they differ only in LoRA rank (run 2 = "a second LoRA rank")."""
import os

BASE_MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
DATASET = "lambdalabs/naruto-blip-captions"
DATA_DIR = os.environ.get("P2_DATA_DIR", "data/p2")
OUT_DIR = os.environ.get("P2_OUT_DIR", "outputs/p2")
SEED = 266
RESOLUTION = 512
TEST_FRACTION = 0.10

TRAIN_COMMON = dict(steps=1500, batch_size=2, grad_accum=2, lr=1e-4, warmup=100, resolution=RESOLUTION,
                    seed=SEED, random_flip=True, grad_checkpointing=True)
RUNS = {
    "run1_lora_r8": dict(rank=8, alpha=8),
    "run2_lora_r32": dict(rank=32, alpha=32),
}

GEN = dict(steps=30, guidance=7.5, height=512, width=512, seeds=(0, 1), scheduler="DPMSolverMultistep")

# Hugging Face repos (edit to your account / team organization)
HF_USER = os.environ.get("HF_USER", "your-hf-username")
HF_MODEL_REPOS = {name: f"{HF_USER}/data266-lab2-naruto-{name.replace('_', '-')}" for name in RUNS}
HF_IMAGES_REPO = f"{HF_USER}/data266-lab2-p2-generations"
