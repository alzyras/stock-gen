import logging
import os
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)

META_CATEGORIZER_PROMPT = """
Categorize input based on prompt and title information, and return a list of categories that best describe the input.
"""


class TaggedCategory(BaseModel):
    """Data model for the categorized image prompt from OpenAI's Chat API.

    Attributes:
        categories str: Category associated with the image prompt.
    """

    categories: Literal[
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
        "No Category Found",
    ]


def get_category(
    theme_prompt: str,
    client: OpenAI,
) -> TaggedCategory:
    """Function which takes in a theme prompt and returns prepared picture prompt and additional metadata."""
    LOGGER.info(f"Getting category for theme: {theme_prompt}")
    return (
        client.beta.chat.completions.parse(
            model=os.environ["OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": META_CATEGORIZER_PROMPT},
                {"role": "user", "content": theme_prompt},
            ],
            response_format=TaggedCategory,
        )
        .choices[0]
        .message.parsed
    )
