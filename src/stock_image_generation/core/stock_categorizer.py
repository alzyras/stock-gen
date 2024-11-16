import os

from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

META_CATEGORIZER_PROMPT = """
Categorize input based on prompt and title information, and return a list of categories that best describe the input.
"""


class TaggedCategories(BaseModel):
    """Data model for the parsed image prompt from OpenAI's Chat API.

    Attributes:
        categories (list[str]): Tags associated with the image prompt.
    """
    categories: list[Literal[
    "Animals",
    "Buildings and Architecture",
    "Business",
    "Drinks",
    "The Environment",
    "States of Mind",
    "Food",
    "Graphic Resources",
    "Hobbies and Leisure",
    "Industry",
    "Landscape",
    "Lifestyle",
    "People",
    "Plants and Flowers",
    "Culture and Religion",
    "Science",
    "Social Issues",
    "Sports",
    "Technology",
    "Transport",
    "Travel",
]]



def get_categories(
    theme_prompt: str,
    client: OpenAI,
) -> TaggedCategories:
    """Function which takes in a theme prompt and returns prepared picture prompt and additional metadata."""
    return (
        client.beta.chat.completions.parse(
            model=os.environ["OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": META_CATEGORIZER_PROMPT},
                {"role": "user", "content": theme_prompt},
            ],
            response_format=TaggedCategories,
        )
        .choices[0]
        .message.parsed
    )
