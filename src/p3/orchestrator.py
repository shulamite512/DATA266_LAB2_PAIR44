"""3.2 Orchestration in plain Python: one typed state, a bounded revise loop (<= 2 revisions),
a JSON trace per request, and clear messages instead of crashes."""
import os
import time
import traceback
import uuid

import torch

from .agents import CritiqueAgent, Generator, Planner, PromptAgent, VisionAgent
from .config import P3Config
from .state import PipelineState, TraceStep


def _summ(state):
    return {"route": state.route, "status": state.status, "revisions": state.revisions,
            "request": state.user_request[:200], "image": os.path.basename(state.image_path or "")}


class MultiAgentSystem:
    def __init__(self, cfg=None, vlm=None, clip=None, nsfw=None):
        from src.common.clip_utils import ClipScorer
        from src.common.safety import NSFWChecker
        from src.common.vlm import VLM
        self.cfg = cfg or P3Config()
        self.vlm = vlm or VLM(self.cfg.vlm_model, load_in_4bit=self.cfg.vlm_4bit)
        self.clip = clip or ClipScorer(self.cfg.clip_model)
        self.nsfw = nsfw or NSFWChecker()
        self.planner = Planner(self.vlm, self.cfg)
        self.vision = VisionAgent(self.vlm)
        self.prompter = PromptAgent(self.vlm, self.cfg)
        self.generator = Generator(self.cfg)
        self.critic = CritiqueAgent(self.vlm, self.clip, self.nsfw, self.cfg)

    def _step(self, state, name, fn, cache):
        t0 = time.time()
        inp = _summ(state)
        try:
            out = fn(state, cache)
            state.trace.append(TraceStep(name, inp, out, round(time.time() - t0, 3)))
            return out
        except torch.cuda.OutOfMemoryError as e:
            torch.cuda.empty_cache()
            err = "GPU ran out of memory"
        except Exception as e:  # never crash: report a clear message
            err = f"{type(e).__name__}: {e}"
        state.trace.append(TraceStep(name, inp, {}, round(time.time() - t0, 3), error=err + "\n" + traceback.format_exc(limit=3)))
        state.status = "error"
        state.message = f"The {name} step failed ({err}). Please try again with a different image or request."
        return None

    def run(self, request, image_path=None, use_critique=True, request_id=None):
        t0 = time.time()
        state = PipelineState(request_id=request_id or uuid.uuid4().hex[:10], user_request=request or "",
                              image_path=image_path, use_critique=use_critique)
        cache = {}
        self._step(state, "planner", self.planner, cache)
        if state.status == "running" and cache.get("image") is not None:
            self._step(state, "vision_understanding", self.vision, cache)
        while state.status == "running":
            if self._step(state, "prompt_engineering", self.prompter, cache) is None:
                break
            if self._step(state, "image_generation", self.generator, cache) is None:
                break
            if use_critique:
                crit = self._step(state, "critique", self.critic, cache)
            else:
                crit = self._step(state, "output_safety_check", lambda s, c: self.critic.safety_only(s), cache)
            if crit is None:
                break
            last_img = state.generations[-1]["image_path"]
            if crit["decision"] == "blocked":
                state.status, state.message = "blocked", "The generated image was flagged as unsafe and has been withheld."
            elif crit["decision"] == "accept":
                state.status, state.final_image_path = "done", last_img
                state.message = f"Done ({state.generations[-1]['mode']}, {state.revisions} revision(s))."
            elif state.revisions < self.cfg.max_revisions:
                state.revisions += 1
            else:
                state.status, state.final_image_path = "done", last_img
                state.message = (f"Returned the best effort after {state.revisions} revisions; the critic still had "
                                 f"concerns: {crit.get('reason', '')}")
        state.total_seconds = round(time.time() - t0, 2)
        state.save(os.path.join(self.cfg.out_dir, "traces"))
        return state
