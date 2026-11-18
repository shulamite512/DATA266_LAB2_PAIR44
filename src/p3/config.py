import os
from dataclasses import dataclass, field


@dataclass
class P3Config:
    vlm_model: str = "Qwen/Qwen2.5-VL-3B-Instruct"   # same VLM as Part 1
    vlm_4bit: bool = False
    base_model: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    # Part 2 LoRA from Hugging Face (set P3_LORA_REPO), or a local folder as fallback
    lora_repo: str = field(default_factory=lambda: os.environ.get("P3_LORA_REPO", "outputs/p2/models/run1_lora_r8"))
    pix2pix_model: str = "timbrooks/instruct-pix2pix"
    clip_model: str = "openai/clip-vit-base-patch16"
    out_dir: str = field(default_factory=lambda: os.environ.get("P3_OUT_DIR", "outputs/p3"))
    seed: int = 266
    sd_steps: int = 30
    pix2pix_steps: int = 20
    guidance: float = 7.5
    style_strength: float = 0.6
    domain_strength: float = 0.65
    image_guidance: float = 1.5
    domain_suffix: str = ", naruto anime style, cel shading"
    clip_accept: float = 0.25      # CLIP cosine threshold used by the critic
    max_revisions: int = 2
    min_side: int = 64
    blank_std: float = 4.0
