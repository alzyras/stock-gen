from openai import OpenAI
from pydantic import BaseModel

from prompt_to_video.core.prompt.video_script import VideoScript
from prompt_to_video.settings import (
    TEXT_GENERATION_MODEL,
    VIDEO_SCRIPT_GENERATION_SYSTEM_PROMPT,
)


class ImagePrompts(BaseModel):
    """Class for image prompt, which is used to generate image."""

    prompts: list[str]


def generate_image_prompts(
    video_script: VideoScript,
    user_prompt: str,
    client: OpenAI,
) -> ImagePrompts:
    """Function which takes video idea prompt and returns prepared video script."""
    return (
        client.beta.chat.completions.parse(
            model=TEXT_GENERATION_MODEL,
            messages=[
                {"role": "system", "content": VIDEO_SCRIPT_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
                {"role": "system", "content": str(video_script)},
                {
                    "role": "user",
                    "content": "Based on the video script, generate image prompts from scenes, be detailed, as it will be used as standalone prompts, and context from the video script will be lost. Each scene should correspond to one prompt.",
                },
            ],
            response_format=ImagePrompts,
        )
        .choices[0]
        .message.parsed
    )
