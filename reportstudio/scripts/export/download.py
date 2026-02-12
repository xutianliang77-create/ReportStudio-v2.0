"""Download metadata helper for generated report artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import hashlib


def build_download_info(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"artifact not found: {file_path}")
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return {
        "status": "ready",
        "file": str(file_path),
        "size": file_path.stat().st_size,
        "sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Get downloadable artifact metadata")
    parser.add_argument("--file", required=True, help="artifact file path")
    args = parser.parse_args()

    info = build_download_info(Path(args.file))
    print(json.dumps(info, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
