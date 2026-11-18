"""Push LoRA adapters (with model card) and the generated-image dataset to Hugging Face.
Requires HF_TOKEN (Kaggle secret / Colab userdata / `huggingface-cli login`)."""
import os

MODEL_CARD = """---
license: creativeml-openrail-m
base_model: {base}
datasets:
- {dataset}
tags: [stable-diffusion, lora, text-to-image, diffusers, data266]
---
# {repo} - SD 1.5 LoRA ({run})

**Base model:** `{base}` (512x512). **Method:** {method}, rank {rank}, alpha {alpha}, UNet attention (`{targets}`).

**Data:** `{dataset}` - {train_images} training images after removing corrupted/duplicate images; 10% test split held out (seed 266).
Naruto characters are copyrighted: **this adapter is for non-commercial research and teaching only.**

**Training:** {steps} steps, batch {batch_size} x grad-accum {grad_accum}, LR {lr} ({schedule}), fp16 mixed precision,
seed {seed}. Trainable parameters: {params:,}. Peak GPU memory {mem} GB, {gpu_hours} GPU-hours on {gpu}.

**Results (from notebooks/p2_finetune.ipynb):**
```
{results}
```

**Limitations:** captions are BLIP auto-captions (short, generic, sometimes wrong); style is narrow (anime faces dominate),
so out-of-domain prompts drift toward Naruto-like faces; compositional prompts (counts, colour binding) are unreliable;
KID is noisy with 20 images. Outputs pass through the SD safety checker; it is not a complete NSFW filter.

**Usage:**
```python
pipe = StableDiffusionPipeline.from_pretrained("{base}", torch_dtype=torch.float16).to("cuda")
pipe.load_lora_weights("{repo}")
```
"""


def push_lora(folder, repo_id, card_fields=None, private=False):
    from huggingface_hub import HfApi, create_repo
    create_repo(repo_id, exist_ok=True, repo_type="model", private=private)
    if card_fields:
        with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
            f.write(MODEL_CARD.format(repo=repo_id, **card_fields))
    HfApi().upload_folder(folder_path=folder, repo_id=repo_id, repo_type="model")
    return f"https://huggingface.co/{repo_id}"


def push_images(meta, repo_id, private=False):
    from datasets import Dataset, Image
    cols = ["file", "model", "prompt_id", "category", "prompt", "seed", "steps", "guidance", "scheduler", "nsfw_flagged"]
    ds = Dataset.from_pandas(meta[cols].rename(columns={"file": "image"}).reset_index(drop=True))
    ds = ds.cast_column("image", Image())
    ds.push_to_hub(repo_id, private=private)
    return f"https://huggingface.co/datasets/{repo_id}"
