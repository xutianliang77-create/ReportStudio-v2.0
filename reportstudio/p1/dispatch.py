"""P1-501~P1-502: 调度分发最小实现。"""

from __future__ import annotations

from datetime import datetime, timezone


def dispatch(summary: dict, channels: list[str] | None = None) -> dict:
    channels = channels or ["internal"]
    return {
        "status": "dispatched",
        "channels": channels,
        "at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }
