import re
from typing import Any


class PromptTemplate:
    """A class to render messages with variables."""

    def __init__(self, messages: list[dict[str, str]]) -> None:
        """Initialize the PromptTemplate object."""
        self.messages = messages
        self.required_vars: list[str] = []
        self._extract_required_vars()

    def _extract_required_vars(self) -> None:
        pattern = r"\{([^{}]+)\}"
        for message in self.messages:
            content = message["content"]
            vars_in_message = re.findall(pattern, content)
            self.required_vars.extend(vars_in_message)
        self.required_vars = list(set(self.required_vars))

    def render(self, **kwargs: dict[str, Any]) -> list[dict[str, str]]:
        """Render the messages with the given variables."""
        missing_vars = set(self.required_vars) - set(kwargs.keys())
        unexpected_vars = set(kwargs.keys()) - set(self.required_vars)
        if missing_vars:
            msg = f"Missing required variables: {', '.join(missing_vars)}"
            raise ValueError(msg)
        if unexpected_vars:
            msg = f"Unexpected variables: {', '.join(unexpected_vars)}"
            raise ValueError(msg)

        formatted_messages = []
        for message in self.messages:
            formatted_content = message["content"].format(**kwargs)
            formatted_messages.append(
                {"role": message["role"], "content": formatted_content},
            )

        return formatted_messages

    def __str__(self) -> str:
        """Return the string representation of the PromptTemplate object."""
        return str(self.messages)
