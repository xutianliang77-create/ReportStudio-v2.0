"""Queue abstraction using RQ+Redis when available, with in-memory fallback."""

from __future__ import annotations

from collections import deque
from typing import Deque

_QUEUE_NAME = "reportstudio_renders"
_LOCAL_QUEUE: Deque[str] = deque()


def _rq_queue():
    try:
        from redis import Redis  # type: ignore
        from rq import Queue  # type: ignore

        conn = Redis(host="localhost", port=6379, db=0)
        return Queue(_QUEUE_NAME, connection=conn)
    except Exception:
        return None


def enqueue_render_job(render_id: str) -> None:
    queue = _rq_queue()
    if queue is None:
        _LOCAL_QUEUE.append(render_id)
    else:
        queue.enqueue("reportstudio.workers.render_worker.process_render_job", render_id)


def dequeue_local_render_job() -> str | None:
    if not _LOCAL_QUEUE:
        return None
    return _LOCAL_QUEUE.popleft()


def queue_backend() -> str:
    return "rq" if _rq_queue() is not None else "memory"
