"""2.2 LoRA fine-tuning of the SD-1.5 UNet (attention projections) on one 16 GB GPU.

A compact version of diffusers' train_text_to_image_lora.py: frozen fp16 VAE/text encoder/UNet,
fp32 LoRA parameters, fp16 autocast + GradScaler, gradient checkpointing. Prints and saves
trainable params, LR, steps, batch size, peak GPU memory and training time.
"""
import json
import math
import os
import random
import time

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from . import config as C
from .data_prep import load_split


class CaptionDataset(Dataset):
    def __init__(self, items, tokenizer, res, flip):
        self.items, self.tok = items, tokenizer
        tf = [transforms.Resize(res), transforms.CenterCrop(res)]
        if flip:
            tf.append(transforms.RandomHorizontalFlip())
        self.tf = transforms.Compose(tf + [transforms.ToTensor(), transforms.Normalize([0.5], [0.5])])

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        path, cap = self.items[i]
        ids = self.tok(cap, padding="max_length", truncation=True, max_length=self.tok.model_max_length,
                       return_tensors="pt").input_ids[0]
        return {"pixel_values": self.tf(Image.open(path).convert("RGB")), "input_ids": ids}


def train(run_name, rank, alpha=None, steps=1500, batch_size=2, grad_accum=2, lr=1e-4, warmup=100,
          resolution=512, seed=C.SEED, random_flip=True, grad_checkpointing=True, use_dora=False,
          base=C.BASE_MODEL, data_dir=C.DATA_DIR, out_dir=C.OUT_DIR, log_every=50):
    from diffusers import AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel
    from diffusers.optimization import get_scheduler
    from diffusers.utils import convert_state_dict_to_diffusers
    from peft import LoraConfig
    from peft.utils import get_peft_model_state_dict
    from transformers import CLIPTextModel, CLIPTokenizer

    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    device, wdtype = "cuda", torch.float16
    tok = CLIPTokenizer.from_pretrained(base, subfolder="tokenizer")
    te = CLIPTextModel.from_pretrained(base, subfolder="text_encoder", torch_dtype=wdtype).to(device)
    vae = AutoencoderKL.from_pretrained(base, subfolder="vae", torch_dtype=wdtype).to(device)
    unet = UNet2DConditionModel.from_pretrained(base, subfolder="unet", torch_dtype=wdtype).to(device)
    noise_sched = DDPMScheduler.from_pretrained(base, subfolder="scheduler")
    for m in (te, vae, unet):
        m.requires_grad_(False)
    unet.add_adapter(LoraConfig(r=rank, lora_alpha=alpha or rank, init_lora_weights="gaussian",
                                target_modules=["to_k", "to_q", "to_v", "to_out.0"], use_dora=use_dora))
    params = [p for p in unet.parameters() if p.requires_grad]
    for p in params:
        p.data = p.data.float()  # train LoRA weights in fp32
    if grad_checkpointing:
        unet.enable_gradient_checkpointing()
    n_trainable = sum(p.numel() for p in params)

    items = load_split("train", data_dir)
    g = torch.Generator().manual_seed(seed)
    loader = DataLoader(CaptionDataset(items, tok, resolution, random_flip), batch_size=batch_size,
                        shuffle=True, drop_last=True, num_workers=2, generator=g)
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=1e-2)
    sched = get_scheduler("cosine", optimizer=opt, num_warmup_steps=warmup, num_training_steps=steps)
    scaler = torch.cuda.amp.GradScaler()

    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    t0 = time.time()
    step, micro, losses, running = 0, 0, [], 0.0
    unet.train()
    while step < steps:
        for batch in loader:
            px = batch["pixel_values"].to(device, wdtype)
            ids = batch["input_ids"].to(device)
            with torch.no_grad():
                latents = vae.encode(px).latent_dist.sample() * vae.config.scaling_factor
                enc = te(ids)[0]
            noise = torch.randn_like(latents)
            t = torch.randint(0, noise_sched.config.num_train_timesteps, (latents.shape[0],), device=device).long()
            noisy = noise_sched.add_noise(latents, noise, t)
            with torch.autocast("cuda", dtype=torch.float16):
                pred = unet(noisy, t, enc).sample
            loss = F.mse_loss(pred.float(), noise.float()) / grad_accum
            scaler.scale(loss).backward()
            running += loss.item()
            micro += 1
            if micro % grad_accum:
                continue
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)
            sched.step()
            step += 1
            losses.append(running)
            running = 0.0
            if step % log_every == 0 or step == 1:
                print(f"[{run_name}] step {step}/{steps} loss {np.mean(losses[-log_every:]):.4f} "
                      f"lr {sched.get_last_lr()[0]:.2e} {time.time() - t0:.0f}s")
            if step >= steps:
                break
    torch.cuda.synchronize()
    seconds = time.time() - t0
    save_dir = os.path.join(out_dir, "models", run_name)
    os.makedirs(save_dir, exist_ok=True)
    unet = unet.to(torch.float32)
    lora_sd = convert_state_dict_to_diffusers(get_peft_model_state_dict(unet))
    StableDiffusionPipeline.save_lora_weights(save_directory=save_dir, unet_lora_layers=lora_sd,
                                              safe_serialization=True)
    stats = {"run": run_name, "method": "DoRA" if use_dora else "LoRA", "rank": rank, "alpha": alpha or rank,
             "target_modules": "to_q,to_k,to_v,to_out.0", "trainable_params": n_trainable,
             "learning_rate": lr, "lr_schedule": f"cosine, warmup {warmup}", "steps": steps,
             "batch_size": batch_size, "grad_accum": grad_accum, "effective_batch": batch_size * grad_accum,
             "epochs": round(steps * batch_size * grad_accum / len(items), 2), "train_images": len(items),
             "peak_gpu_mem_gb": round(torch.cuda.max_memory_allocated() / 1024 ** 3, 2),
             "train_seconds": round(seconds, 1), "gpu_hours": round(seconds / 3600, 3),
             "gpu": torch.cuda.get_device_name(0), "seed": seed, "final_loss_avg50": float(np.mean(losses[-50:])),
             "losses": [float(x) for x in losses]}
    with open(os.path.join(save_dir, "train_stats.json"), "w") as f:
        json.dump(stats, f, indent=1)
    print({k: v for k, v in stats.items() if k != "losses"})
    del unet, vae, te, opt
    torch.cuda.empty_cache()
    return stats
