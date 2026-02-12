"""Utilities for generating OpenClaw skill assets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillExample:
    """Example interaction that demonstrates how to use a skill."""

    prompt: str
    response: str


@dataclass(frozen=True)
class SkillSpec:
    """Structured content for an OpenClaw skill."""

    name: str
    summary: str
    when_to_use: tuple[str, ...]
    workflow: tuple[str, ...]
    examples: tuple[SkillExample, ...] = ()


def _render_bullet_list(items: tuple[str, ...]) -> list[str]:
    """Render a tuple of strings as markdown bullets."""
    return [f"- {item}" for item in items]


def render_skill_markdown(spec: SkillSpec) -> str:
    """Render a complete OpenClaw-compatible ``SKILL.md`` document."""
    lines: list[str] = [
        f"# {spec.name}",
        "",
        "## Summary",
        spec.summary,
        "",
        "## When to use",
    ]
    lines.extend(_render_bullet_list(spec.when_to_use))

    lines.extend(["", "## Workflow"])
    for index, step in enumerate(spec.workflow, start=1):
        lines.append(f"{index}. {step}")

    if spec.examples:
        lines.extend(["", "## Examples"])
        for example in spec.examples:
            lines.extend(
                [
                    "",
                    "### Prompt",
                    example.prompt,
                    "",
                    "### Response",
                    example.response,
                ]
            )

    return "\n".join(lines)


def render_skill_package(spec: SkillSpec) -> dict[str, str]:
    """Build a minimal file package for an OpenClaw skill directory."""
    return {
        "SKILL.md": render_skill_markdown(spec),
        "README.md": f"# {spec.name}\n\n{spec.summary}",
    }
