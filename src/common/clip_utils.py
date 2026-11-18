"""CLIP helpers: prompt/image similarity (Part 2 CLIP score, Part 3 critique) and
image-image similarity (Part 2 memorization check)."""
import torch
import torch.nn.functional as F
from PIL import Image

DEFAULT_CLIP = "openai/clip-vit-base-patch16"


def _load(x):
    return x.convert("RGB") if isinstance(x, Image.Image) else Image.open(x).convert("RGB")


class ClipScorer:
    def __init__(self, model_id=DEFAULT_CLIP, device=None):
        from transformers import CLIPModel, CLIPProcessor
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CLIPModel.from_pretrained(model_id).to(self.device).eval()
        self.proc = CLIPProcessor.from_pretrained(model_id)
        self.model_id = model_id

    @torch.inference_mode()
    def image_embeds(self, images, batch_size=32):
        outs = []
        for i in range(0, len(images), batch_size):
            batch = [_load(x) for x in images[i:i + batch_size]]
            inp = self.proc(images=batch, return_tensors="pt").to(self.device)
            outs.append(F.normalize(self.model.get_image_features(**inp).float(), dim=-1).cpu())
        return torch.cat(outs)

    @torch.inference_mode()
    def text_embeds(self, texts, batch_size=64):
        outs = []
        for i in range(0, len(texts), batch_size):
            inp = self.proc(text=list(texts[i:i + batch_size]), return_tensors="pt", padding=True,
                            truncation=True, max_length=77).to(self.device)
            outs.append(F.normalize(self.model.get_text_features(**inp).float(), dim=-1).cpu())
        return torch.cat(outs)

    def cosine(self, images, texts):
        """Cosine similarity of each image with its own text (paired lists)."""
        return (self.image_embeds(images) * self.text_embeds(texts)).sum(-1)

    def clip_score(self, images, texts):
        """CLIPScore as in Hessel et al. / torchmetrics: 100 * max(cos, 0)."""
        return (100 * self.cosine(images, texts).clamp(min=0)).tolist()
