import pytest

from prompt_to_video.core.prompt.prompt_template import PromptTemplate


def test_render_replaces_required_variables() -> None:
    template = PromptTemplate(
        [
            {"role": "system", "content": "Write for {audience}."},
            {"role": "user", "content": "Topic: {topic}"},
        ],
    )

    assert template.required_vars == ["audience", "topic"]
    assert template.render(audience="beginners", topic="history") == [
        {"role": "system", "content": "Write for beginners."},
        {"role": "user", "content": "Topic: history"},
    ]


def test_render_rejects_missing_or_unexpected_variables() -> None:
    template = PromptTemplate([{"role": "user", "content": "Topic: {topic}"}])

    with pytest.raises(ValueError, match="Missing required variables"):
        template.render()

    with pytest.raises(ValueError, match="Unexpected variables"):
        template.render(topic="history", extra="nope")
