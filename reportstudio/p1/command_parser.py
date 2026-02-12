"""P1-701: deterministic command parsing for ReportStudio scaffold."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ParsedCommand:
    intent: str
    endpoint: str


_RULES: list[tuple[re.Pattern[str], ParsedCommand]] = [
    (re.compile(r"^(create|make|生成|创建)\s+(report|报表)$", re.IGNORECASE), ParsedCommand("report.create", "reports.create")),
    (re.compile(r"^(render|导出)\s+(json|xlsx|pdf)$", re.IGNORECASE), ParsedCommand("report.export", "renders.create")),
    (re.compile(r"^(download|下载)\s+artifact$", re.IGNORECASE), ParsedCommand("report.download", "artifacts.get")),
]


def parse_command(command: str) -> ParsedCommand:
    normalized = " ".join(command.strip().split())
    for pattern, parsed in _RULES:
        if pattern.match(normalized):
            return parsed
    raise ValueError(f"Unsupported command: {command}")
