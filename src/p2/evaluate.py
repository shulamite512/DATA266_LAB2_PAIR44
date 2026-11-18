"""2.4 Evaluation: KID, CLIP score, LPIPS diversity, blinded human pairs, memorization check."""
import os
import random

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from . import config as C


def _to_tensor(paths, size):
    import torch  # imported here so the human-evaluation helpers also work on a CPU-only machine
    arr = [np.asarray(Image.open(p).convert("RGB").resize((size, size), Image.BICUBIC)) for p in paths]
    return torch.from_numpy(np.stack(arr)).permute(0, 3, 1, 2)


def kid(real_paths, fake_paths, subset_size=None, subsets=100, seed=C.SEED):
    import torch
    from torchmetrics.image.kid import KernelInceptionDistance
    torch.manual_seed(seed)
    ss = subset_size or min(len(real_paths), len(fake_paths))
    m = KernelInceptionDistance(subset_size=ss, subsets=subsets, normalize=True).to("cuda")
    for paths, real in ((real_paths, True), (fake_paths, False)):
        for i in range(0, len(paths), 16):
            x = _to_tensor(paths[i:i + 16], 299).float().div(255).to("cuda")
            m.update(x, real=real)
    mean, std = m.compute()
    return float(mean), float(std)


def lpips_diversity(meta, model):
    import lpips
    import torch
    fn = lpips.LPIPS(net="alex", verbose=False).to("cuda")
    sub = meta[meta.model == model]
    d = []
    for pid, grp in sub.groupby("prompt_id"):
        files = grp.sort_values("seed").file.tolist()
        if len(files) < 2:
            continue
        x = _to_tensor(files[:2], 256).float().div(127.5).sub(1).to("cuda")
        with torch.no_grad():
            d.append(float(fn(x[0:1], x[1:2]).item()))
    return float(np.mean(d)), d


def make_human_pairs(meta, final_model, base_model="base", n=25, seed=C.SEED,
                     out_dir=os.path.join(C.OUT_DIR, "human_eval")):
    """Blinded pairs: left/right randomized. key.csv must not be opened by raters."""
    os.makedirs(out_dir, exist_ok=True)
    rng = random.Random(seed)
    keys = meta[meta.model == final_model][["prompt_id", "seed", "prompt"]].values.tolist()
    rng.shuffle(keys)
    rows = []
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    for k, (pid, seed_, prompt) in enumerate(keys[:n]):
        f = meta[(meta.model == final_model) & (meta.prompt_id == pid) & (meta.seed == seed_)].file.iloc[0]
        b = meta[(meta.model == base_model) & (meta.prompt_id == pid) & (meta.seed == seed_)].file.iloc[0]
        left_is_final = rng.random() < 0.5
        L, R = (f, b) if left_is_final else (b, f)
        canvas = Image.new("RGB", (1044, 600), "white")
        canvas.paste(Image.open(L).resize((512, 512)), (0, 0))
        canvas.paste(Image.open(R).resize((512, 512)), (532, 0))
        dr = ImageDraw.Draw(canvas)
        dr.text((240, 520), "A (left)", fill="black", font=font)
        dr.text((770, 520), "B (right)", fill="black", font=font)
        dr.text((10, 560), f"Prompt: {prompt[:110]}", fill="black", font=font)
        name = f"pair_{k:02d}.png"
        canvas.save(os.path.join(out_dir, name))
        rows.append({"pair_id": k, "file": name, "prompt": prompt, "prompt_id": pid, "seed": seed_,
                     "left_model": final_model if left_is_final else base_model,
                     "right_model": base_model if left_is_final else final_model})
    key = pd.DataFrame(rows)
    key.to_csv(os.path.join(out_dir, "key.csv"), index=False)
    return key


def human_win_rate(key, ratings_path="eval/p2_human_ratings.csv", final_model=None):
    """ratings: rater, pair_id, style_choice (A/B), prompt_choice (A/B)."""
    if not os.path.exists(ratings_path):
        return None
    r = pd.read_csv(ratings_path).dropna(subset=["style_choice", "prompt_choice"])
    if r.empty:
        return None
    r = r.merge(key[["pair_id", "left_model"]], on="pair_id")
    final_model = final_model or key.left_model[key.left_model != "base"].iloc[0]
    out = {"raters": r.rater.nunique(), "judgements": len(r)}
    for crit in ("style_choice", "prompt_choice"):
        chose_final = ((r[crit].str.upper() == "A") == (r.left_model == final_model))
        out[f"{crit}_final_win_rate"] = round(float(chose_final.mean()), 3)
        maj = chose_final.groupby(r.pair_id).mean()
        out[f"{crit}_majority_win_rate"] = round(float((maj > 0.5).mean()), 3)
    return out


def memorization(clip, gen_paths, train_paths, k=3):
    """For each generated image find the most similar training image (CLIP image cosine)."""
    g = clip.image_embeds(gen_paths)
    t = clip.image_embeds(train_paths)
    sims = g @ t.T
    best, idx = sims.max(dim=1)
    rows = [{"generated": gen_paths[i], "nearest_train": train_paths[int(idx[i])], "clip_cos": float(best[i])}
            for i in range(len(gen_paths))]
    df = pd.DataFrame(rows).sort_values("clip_cos", ascending=False).reset_index(drop=True)
    return df, df.head(k)
