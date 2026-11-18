"""2.3 Generation: 20 prompts x 2 seeds for the base model and both runs, same sampler
settings; NSFW filter = the pipeline's built-in SD safety checker (kept ON)."""
import gc
import json
import os
import time

import pandas as pd
import torch

from . import config as C


def load_pipe(lora_path=None, base=C.BASE_MODEL):
    from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline
    pipe = StableDiffusionPipeline.from_pretrained(base, torch_dtype=torch.float16).to("cuda")
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.set_progress_bar_config(disable=True)
    if lora_path:
        pipe.load_lora_weights(lora_path)
    return pipe


def generate_all(models, prompts, out_dir=os.path.join(C.OUT_DIR, "generations"), gen=C.GEN):
    """models: {name: lora_path_or_None}. Returns a metadata DataFrame."""
    rows = []
    for name, lora in models.items():
        pipe = load_pipe(lora)
        d = os.path.join(out_dir, name)
        os.makedirs(d, exist_ok=True)
        for p in prompts:
            for seed in gen["seeds"]:
                g = torch.Generator("cuda").manual_seed(seed)
                t0 = time.time()
                res = pipe(p["prompt"], num_inference_steps=gen["steps"], guidance_scale=gen["guidance"],
                           height=gen["height"], width=gen["width"], generator=g)
                sec = time.time() - t0
                path = os.path.join(d, f"{p['id']}_s{seed}.png")
                res.images[0].save(path)
                rows.append({"model": name, "lora": lora or "", "prompt_id": p["id"], "category": p["category"],
                             "prompt": p["prompt"], "seed": seed, "steps": gen["steps"], "guidance": gen["guidance"],
                             "scheduler": gen["scheduler"], "nsfw_flagged": bool(res.nsfw_content_detected[0])
                             if res.nsfw_content_detected is not None else False,
                             "seconds": round(sec, 2), "file": path})
        del pipe
        gc.collect()
        torch.cuda.empty_cache()
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "metadata.csv"), index=False)
    return df


def side_by_side(meta, prompt_ids, models, out_path, seed=0):
    import matplotlib.pyplot as plt
    from PIL import Image
    fig, axes = plt.subplots(len(prompt_ids), len(models), figsize=(3.2 * len(models), 3.4 * len(prompt_ids)))
    for i, pid in enumerate(prompt_ids):
        for j, m in enumerate(models):
            row = meta[(meta.model == m) & (meta.prompt_id == pid) & (meta.seed == seed)].iloc[0]
            ax = axes[i, j]
            ax.imshow(Image.open(row.file))
            ax.set_xticks([]); ax.set_yticks([])
            if i == 0:
                ax.set_title(m, fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{pid}\n{row.prompt[:45]}", fontsize=7)
    plt.tight_layout()
    plt.savefig(out_path, dpi=110)
    plt.show()
    return out_path
