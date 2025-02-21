import logging

from openai import OpenAI
from pydantic import BaseModel

from prompt_to_video.settings import (
    TEXT_GENERATION_MODEL,
    VIDEO_SCRIPT_GENERATION_SYSTEM_PROMPT,
)

LOGGER = logging.getLogger(__name__)


class Scene(BaseModel):
    scene_number: int
    description: str

    def __str__(self) -> str:
        """Return a formatted string representation of a scene."""
        return f"  Scene {self.scene_number}: {self.description}\n"


class Chapter(BaseModel):
    title: str
    narrative: str
    scenes: list[Scene]

    def __str__(self) -> str:
        """Return a formatted string representation of a chapter."""
        scenes_str = "\n".join(str(scene) for scene in self.scenes)
        return f"Chapter: {self.title}\nNarrative: {self.narrative}\n{scenes_str}"


class VideoScript(BaseModel):
    title: str
    chapters: list[Chapter]

    def __str__(self) -> str:
        """Return a formatted string representation of a video script."""
        chapters_str = "\n\n".join(str(chapter) for chapter in self.chapters)
        return f"VideoScript: {self.title}\n\n{chapters_str}"

    def get_full_narrative(self) -> str:
        """Return the full narrative of the video script."""
        return "\n".join(chapter.narrative for chapter in self.chapters)

    def get_all_scenes(self) -> list[Scene]:
        """Return a list of all scenes in the video script."""
        return [scene for chapter in self.chapters for scene in chapter.scenes]


def generate_video_script(
    user_prompt: str,
    client: OpenAI,
) -> VideoScript:
    """Function which takes video idea prompt and returns prepared video script."""
    return (
        client.beta.chat.completions.parse(
            model=TEXT_GENERATION_MODEL,
            messages=[
                {"role": "system", "content": VIDEO_SCRIPT_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=VideoScript,
        )
        .choices[0]
        .message.parsed
    )
