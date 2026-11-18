"""One shared, typed state passed between the five agents (3.2.1)."""
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

ROUTES = ("caption_question", "style_change", "edit", "domain_style", "unsupported", "ambiguous")


@dataclass
class TraceStep:
    agent: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    seconds: float
    error: Optional[str] = None


@dataclass
class PipelineState:
    request_id: str
    user_request: str
    image_path: Optional[str] = None
    use_critique: bool = True
    # planner
    route: str = ""
    image_ok: bool = False
    image_problem: str = ""
    refused: bool = False
    refusal_reason: str = ""
    planner: Dict[str, Any] = field(default_factory=dict)
    # vision
    vision: Dict[str, Any] = field(default_factory=dict)
    # prompt engineering / generation / critique, one entry per attempt
    prompts: List[Dict[str, Any]] = field(default_factory=list)
    generations: List[Dict[str, Any]] = field(default_factory=list)
    critiques: List[Dict[str, Any]] = field(default_factory=list)
    revisions: int = 0
    # result
    status: str = "running"   # done | refused | error | clarification_needed | blocked
    message: str = ""
    final_image_path: str = ""
    trace: List[TraceStep] = field(default_factory=list)
    total_seconds: float = 0.0

    def to_dict(self):
        return asdict(self)

    def save(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{self.request_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=1, ensure_ascii=False, default=str)
        return path
