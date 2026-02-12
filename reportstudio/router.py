"""Intent routing helper for ReportStudio skill scaffolding."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


class UnknownIntentError(ValueError):
    """Raised when an intent is not mapped to any script entrypoint."""


@dataclass(frozen=True)
class IntentRoute:
    intent: str
    script: str
    module: str


DEFAULT_ROUTES_PATH = Path(__file__).with_name("config") / "intent_routes.json"


def load_routes(path: Path = DEFAULT_ROUTES_PATH) -> Dict[str, IntentRoute]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    routes: Dict[str, IntentRoute] = {}
    for entry in payload.get("routes", []):
        route = IntentRoute(
            intent=entry["intent"],
            script=entry["script"],
            module=entry["module"],
        )
        routes[route.intent] = route
    return routes


def resolve_intent(intent: str, path: Path = DEFAULT_ROUTES_PATH) -> IntentRoute:
    routes = load_routes(path)
    try:
        return routes[intent]
    except KeyError as exc:
        raise UnknownIntentError(f"Unknown intent: {intent}") from exc


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a ReportStudio intent route")
    parser.add_argument("intent", help="intent name, e.g. report.create")
    args = parser.parse_args()

    route = resolve_intent(args.intent)
    print(json.dumps(route.__dict__, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
