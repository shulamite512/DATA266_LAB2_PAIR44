"""Thin wrapper around a local vision-language model (default Qwen2.5-VL-3B-Instruct).

Used by Part 1 (figure descriptions + answer generation) and Part 3 (planner, vision,
prompt engineering and critique agents). Runs on one 16 GB GPU in fp16, or in 4-bit
with bitsandbytes when memory is tight.
"""
import json
import re

import torch
from PIL import Image

DEFAULT_VLM = "Qwen/Qwen2.5-VL-3B-Instruct"


class VLM:
    supports_images = True

    def __init__(self, model_id=DEFAULT_VLM, load_in_4bit=False, max_pixels=1024 * 28 * 28,
                 min_pixels=128 * 28 * 28, dtype=torch.float16):
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
        kwargs = dict(torch_dtype=dtype, device_map="auto", attn_implementation="sdpa")
        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=dtype)
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id, **kwargs).eval()
        self.processor = AutoProcessor.from_pretrained(model_id, min_pixels=min_pixels, max_pixels=max_pixels)
        self.model_id = model_id

    @staticmethod
    def _to_pil(img):
        if isinstance(img, Image.Image):
            return img.convert("RGB")
        return Image.open(img).convert("RGB")

    @torch.inference_mode()
    def chat(self, user_text, images=(), system=None, max_new_tokens=384):
        """Greedy (deterministic) generation. `images` are PIL images or file paths."""
        pil = [self._to_pil(i) for i in images]
        content = [{"type": "image"} for _ in pil] + [{"type": "text", "text": user_text}]
        messages = []
        if system:
            messages.append({"role": "system", "content": [{"type": "text", "text": system}]})
        messages.append({"role": "user", "content": content})
        prompt = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[prompt], images=pil or None, return_tensors="pt").to(self.model.device)
        out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                                  temperature=None, top_p=None, top_k=None)
        new = out[:, inputs["input_ids"].shape[1]:]
        return self.processor.batch_decode(new, skip_special_tokens=True)[0].strip()

    def chat_json(self, user_text, images=(), system=None, max_new_tokens=384, default=None):
        raw = self.chat(user_text, images, system, max_new_tokens)
        parsed = parse_json(raw)
        return (parsed if parsed is not None else default), raw


class TextLLM(VLM):
    """Text-only answer model (default Qwen3-14B, 4-bit). Used after ingestion, when figures are already
    described in text; images passed to chat() are ignored."""
    supports_images = False

    def __init__(self, model_id="Qwen/Qwen3-14B", load_in_4bit=True, thinking=False, dtype=torch.float16):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        kwargs = dict(torch_dtype=dtype, device_map="auto", low_cpu_mem_usage=True)
        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=dtype)
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs).eval()
        self.model_id, self.thinking = model_id, thinking

    @torch.inference_mode()
    def chat(self, user_text, images=(), system=None, max_new_tokens=384):
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user_text}]
        prompt = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                              enable_thinking=self.thinking)
        inputs = self.tok([prompt], return_tensors="pt").to(self.model.device)
        out = self.model.generate(**inputs, max_new_tokens=max_new_tokens * (6 if self.thinking else 1),
                                  do_sample=False, temperature=None, top_p=None, top_k=None)
        text = self.tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


class ClaudeVLM(VLM):
    """Hosted backend with the same chat()/chat_json() interface (Anthropic Messages API, vision).
    Needs ANTHROPIC_API_KEY. Declared in README with its model ID when used."""

    def __init__(self, model_id="claude-opus-5-5", effort=None):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model_id = model_id
        self.effort = effort or __import__("os").environ.get("CLAUDE_EFFORT", "medium")

    def chat(self, user_text, images=(), system=None, max_new_tokens=384):
        import base64
        import io
        content = []
        for img in images:
            buf = io.BytesIO()
            self._to_pil(img).save(buf, format="PNG")
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                        "data": base64.standard_b64encode(buf.getvalue()).decode()}})
        content.append({"type": "text", "text": user_text})
        kwargs = dict(model=self.model_id, max_tokens=16000, output_config={"effort": self.effort},
                      messages=[{"role": "user", "content": content}])
        if system:
            kwargs["system"] = system
        try:
            # server-side fallback: if a request is declined by a safety classifier, the API retries it on
            # a fallback model inside the same call
            resp = self.client.beta.messages.create(betas=["server-side-fallback-2026-07-01"],
                                                    fallbacks="default", **kwargs)
        except Exception as e:  # keep the pipeline running; the caller treats "" as no answer
            print("Claude API error:", type(e).__name__, str(e)[:200])
            return ""
        if resp.stop_reason == "refusal":
            return ""
        return "".join(b.text for b in resp.content if b.type == "text").strip()


class GeminiVLM(VLM):
    """Hosted backend via the google-genai SDK (free-tier API key from Google AI Studio).
    Needs GEMINI_API_KEY. Paced to stay under free-tier request limits."""

    def __init__(self, model_id="gemini-4-hydrogen", min_interval=6.5):
        import os
        from google import genai
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model_id = model_id
        self.min_interval = float(os.environ.get("GEMINI_MIN_INTERVAL", min_interval))
        self._last = 0.0

    def _pick_available_model(self):
        names = [m.name.split("/")[-1] for m in self.client.models.list()]
        flash = [n for n in names if "flash" in n and "lite" not in n and "image" not in n and "tts" not in n]
        return (sorted(flash) or names)[-1]

    def chat(self, user_text, images=(), system=None, max_new_tokens=384):
        import time
        from google.genai import types
        contents = [self._to_pil(i) for i in images] + [user_text]
        config = types.GenerateContentConfig(system_instruction=system, temperature=0.0, max_output_tokens=8192)
        for attempt in range(6):
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                resp = self.client.models.generate_content(model=self.model_id, contents=contents, config=config)
                return (resp.text or "").strip()
            except Exception as e:
                msg = str(e)
                if ("404" in msg or "not found" in msg.lower()) and attempt == 0:
                    self.model_id = self._pick_available_model()
                    print("Gemini model not available; switched to", self.model_id)
                elif "429" in msg or "RESOURCE_EXHAUSTED" in msg or "503" in msg or "UNAVAILABLE" in msg:
                    print(f"  Gemini busy/quota ({msg[:120]}); retry {attempt + 1}/5 in {20 * (attempt + 1)}s", flush=True)
                    if "per day" in msg.lower() or "PerDay" in msg:
                        print("  DAILY free quota used up - wait until tomorrow, use another key, or switch BACKEND.")
                        return ""
                    time.sleep(20 * (attempt + 1))
                else:
                    print("Gemini API error:", type(e).__name__, msg[:200])
                    return ""
        return ""


def make_vlm(model_id, load_in_4bit=False):
    """P1_BACKEND=claude|gemini -> hosted backend, otherwise the local Qwen VLM."""
    import os
    backend = os.environ.get("P1_BACKEND", "local")
    if backend == "claude":
        return ClaudeVLM(model_id if model_id.startswith("claude") else "claude-opus-5-5")
    if backend == "gemini":
        return GeminiVLM(model_id if model_id.startswith("gemini") else "gemini-4-hydrogen")
    return VLM(model_id, load_in_4bit=load_in_4bit)


def parse_json(text):
    """Return the first balanced JSON object found in `text`, or None."""
    if not text:
        return None
    text = re.sub(r"```(?:json)?", "", text)
    start = text.find("{")
    while start >= 0:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    cand = text[start:i + 1]
                    for attempt in (cand, re.sub(r",\s*([}\]])", r"\1", cand)):
                        try:
                            return json.loads(attempt)
                        except json.JSONDecodeError:
                            pass
                    break
        start = text.find("{", start + 1)
    return None
