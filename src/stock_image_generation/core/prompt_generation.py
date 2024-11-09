import os
from pathlib import Path

from openai import OpenAI
from PIL import Image
from pydantic import BaseModel

META_PROMPT = """
You are a skilled prompt creator for an advanced image generation system. Your task is to construct precise, vivid prompts that enable the AI to generate images with exceptional clarity, detail, and realism. Each prompt should convey a fully realized vision, capturing the intended subject, environment, and atmosphere with maximum specificity and depth.

Your prompts will demonstrate:

Accuracy: Deliver a clear, exact description to eliminate ambiguity, allowing the AI to reproduce each visual element with fidelity.

Rich Detail: Include comprehensive, nuanced details that add realism and complexity, enabling the AI to capture all essential aspects of the scene.

Depth & Coherence: Build a well-defined prompt structure that guides the AI in rendering a cohesive, lifelike image aligned with the intended vision.

Each prompt should reflect your expertise in translating complex visual concepts into precise language, empowering the AI to create images of outstanding quality.
"""


class PicturePrompt(BaseModel):
    title: str
    description: str
    tags: list[str]
    generation_prompt: str


class PictureData(PicturePrompt):
    path: str
    theme_prompt: str

    def load_image(self) -> Image:
        """Function to load the generated image."""
        return Image.open(self.path)


def get_picture_prompt(
    theme_prompt: str,
    image_path: str | Path,
    client: OpenAI,
) -> PictureData:
    """Function which takes in a theme prompt and returns prepared picture prompt and additional metadata."""
    picture_prompt = (
        client.beta.chat.completions.parse(
            model=os.environ["OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": META_PROMPT},
                {"role": "user", "content": theme_prompt},
            ],
            response_format=PicturePrompt,
        )
        .choices[0]
        .message.parsed
    )
    return PictureData(
        title=picture_prompt.title,
        description=picture_prompt.description,
        tags=picture_prompt.tags,
        generation_prompt=picture_prompt.generation_prompt,
        path=str(image_path),
        theme_prompt=theme_prompt,
    )
