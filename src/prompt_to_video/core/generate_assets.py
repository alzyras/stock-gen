import json
import logging
from pathlib import Path
from typing import Any

from prompt_to_video.core.audio.tts import EdgeTTS
from prompt_to_video.core.image import ImageGenerator

LOGGER = logging.getLogger(__name__)


class AssetGenerator:
    """Generate per-scene audio, subtitles, and images from a script JSON file."""

    def __init__(
        self,
        project_folder: str = "other",
        project_storage: str | Path = "store/projects",
        script_path: str | Path = "scripts/prompt.json",
    ) -> None:
        self.project_folder = project_folder
        self.project_storage = Path(project_storage)
        self.script_path = self.project_storage / project_folder / script_path
        self.quantity_each = 1
        self.voice = "en-US-JennyNeural"

    def read_json(self, file_path: str | Path) -> dict[str, Any]:
        with Path(file_path).open(encoding="utf-8") as file:
            return json.load(file)

    def create_folder(self, script_path: str | Path) -> Path:
        folder_name = Path(script_path).stem
        folder_path = self.script_path.parents[1] / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    def generate_audio(
        self,
        script_json: dict[str, Any],
        folder_path: str | Path,
        voice: str = "en-US-JennyNeural",
    ) -> None:
        edge_tts = EdgeTTS()
        output_root = Path(folder_path)

        for scene_number, scene in enumerate(script_json.get("scenes", []), start=1):
            LOGGER.info(
                "Processing scene %s: %s",
                scene_number,
                scene.get("title", "Untitled"),
            )
            scene_folder = output_root / str(scene_number)
            scene_folder.mkdir(parents=True, exist_ok=True)

            audio_file = scene_folder / "audio.mp3"
            srt_file = scene_folder / "subtitles.srt"
            if audio_file.exists():
                LOGGER.info("Audio for scene %s already exists", scene_number)
                continue

            edge_tts.generate_audio(
                text=scene.get("narrative", "No description"),
                voice=voice,
                output_file=audio_file,
                srt_file=srt_file,
            )

    def generate_images(
        self,
        script_json: dict[str, Any],
        folder_path: str | Path,
        quantity_each: int = 1,
    ) -> None:
        image_generator = ImageGenerator()
        output_root = Path(folder_path)

        for scene_number, scene in enumerate(script_json.get("scenes", []), start=1):
            LOGGER.info(
                "Processing scene %s: %s",
                scene_number,
                scene.get("story_title", scene.get("title", "Untitled")),
            )
            scene_folder = output_root / str(scene_number)
            scene_folder.mkdir(parents=True, exist_ok=True)

            for prompt_index, prompt in enumerate(
                scene.get("image_prompts", []), start=1
            ):
                for variant_index in range(quantity_each):
                    image_path = (
                        scene_folder / f"{prompt_index}_{variant_index + 1}.png"
                    )
                    if image_path.exists():
                        LOGGER.info("Image already exists: %s", image_path)
                        continue

                    image_data = image_generator.generate_image(
                        theme_prompt=prompt,
                        subfolder=scene_folder,
                        height=576,
                        width=1024,
                        num_inference_steps=2,
                    )
                    image_data.save_image(image_path)

    def run(self) -> None:
        data = self.read_json(self.script_path)
        folder_path = self.create_folder(self.script_path)
        self.generate_audio(data, folder_path, self.voice)
        self.generate_images(data, folder_path, quantity_each=self.quantity_each)


if __name__ == "__main__":
    generator = AssetGenerator(
        project_folder="historic_facts",
        script_path="scripts/top_5_foods_medieval_england.json",
    )
    generator.voice = "en-GB-RyanNeural"
    generator.quantity_each = 3
    generator.run()
