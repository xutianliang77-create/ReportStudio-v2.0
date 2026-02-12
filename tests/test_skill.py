from reportstudio.skill import SkillExample, SkillSpec, render_skill_markdown, render_skill_package


def test_render_skill_markdown_contains_required_sections() -> None:
    spec = SkillSpec(
        name="openclaw-search",
        summary="Provide consistent repository search and summarization.",
        when_to_use=("When users ask to inspect a codebase quickly.",),
        workflow=("Collect context.", "Summarize findings."),
    )

    markdown = render_skill_markdown(spec)

    assert "# openclaw-search" in markdown
    assert "## Summary" in markdown
    assert "## When to use" in markdown
    assert "## Workflow" in markdown


def test_render_skill_markdown_includes_examples() -> None:
    spec = SkillSpec(
        name="openclaw-test",
        summary="Help author test plans.",
        when_to_use=("When user requests a test strategy.",),
        workflow=("Review requirements.",),
        examples=(
            SkillExample(prompt="Create a smoke test list", response="1. Launch app"),
        ),
    )

    markdown = render_skill_markdown(spec)

    assert "## Examples" in markdown
    assert "### Prompt" in markdown
    assert "Create a smoke test list" in markdown


def test_render_skill_package_returns_skill_and_readme() -> None:
    spec = SkillSpec(
        name="openclaw-docs",
        summary="Draft documentation snippets.",
        when_to_use=("When user asks for docs.",),
        workflow=("Collect API details.",),
    )

    package = render_skill_package(spec)

    assert set(package.keys()) == {"SKILL.md", "README.md"}
    assert package["README.md"].startswith("# openclaw-docs")
