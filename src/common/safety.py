"""NSFW output filter shared by Part 2 and Part 3: the Stable Diffusion safety checker
(CompVis/stable-diffusion-safety-checker) applied to any PIL image."""
import numpy as np
import torch
from PIL import Image


class NSFWChecker:
    def __init__(self, device=None):
        from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
        from transformers import CLIPImageProcessor
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.checker = StableDiffusionSafetyChecker.from_pretrained(
            "CompVis/stable-diffusion-safety-checker", torch_dtype=self.dtype).to(self.device).eval()
        self.fe = CLIPImageProcessor.from_pretrained("openai/clip-vit-base-patch32")

    @torch.inference_mode()
    def __call__(self, images):
        """Return a list of booleans: True = flagged as NSFW."""
        pil = [(i if isinstance(i, Image.Image) else Image.open(i)).convert("RGB").resize((512, 512)) for i in images]
        clip_in = self.fe(pil, return_tensors="pt").pixel_values.to(self.device, self.dtype)
        arr = np.stack([np.asarray(p, dtype=np.float32) / 255.0 for p in pil])
        _, flags = self.checker(images=arr, clip_input=clip_in)
        return [bool(f) for f in flags]
