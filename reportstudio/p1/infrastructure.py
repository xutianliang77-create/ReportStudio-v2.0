"""P1-001~P1-007: 基础设施能力（配置、日志、错误、运行上下文）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid


@dataclass(frozen=True)
class AppConfig:
    workspace_dir: Path = Path("reportstudio/data")
    default_timezone: str = "Asia/Shanghai"


class ReportStudioError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass
class RunContext:
    trace_id: str = field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class JsonLogger:
    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id

    def event(self, action: str, detail: dict | None = None) -> str:
        payload = {
            "trace_id": self.trace_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "detail": detail or {},
        }
        return json.dumps(payload, ensure_ascii=False)


def ensure_workspace(config: AppConfig) -> Path:
    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    return config.workspace_dir
