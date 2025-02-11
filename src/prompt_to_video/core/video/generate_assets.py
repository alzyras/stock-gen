import json
import logging
import os

from prompt_to_video.core.image.text2img_simple import \
    ImageGenerator
from prompt_to_video.core.tts import EdgeTTS

LOGGER = logging.getLogger(__name__)


class AssetGenerator:
    def __init__(self, project_folder="other", project_storage="store/projects/", script_path="scripts/prompt.json"):
        self.project_folder = project_folder
        self.project_storage = project_storage
        self.script_path = os.path.join(project_storage, project_folder, script_path)
        self.quantity_each = 1
        self.voice = "en-US-JennyNeural"

    def read_json(self, file_path):
        with open(file_path, "r") as file:
            return json.load(file)

    def create_folder(self, script_path):
        folder_name = os.path.splitext(os.path.basename(script_path))[0
        project_folder_path = os.path.dirname(os.path.dirname(self.script_path))
        folder_path = os.path.join(project_folder_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def generate_audio(self, script_json, folder_path, voice="en-US-JennyNeural"):
        edge_tts = EdgeTTS()

        for scene_number, scene in enumerate(script_json.get("scenes", []), start=1):
            LOGGER.info(f"Processing scene {scene_number}: {scene.get('title', 'Untitled')}")

            scene_folder = os.path.join(folder_path, str(scene_number))
            os.makedirs(scene_folder, exist_ok=True)

            scene_description = scene.get("narrative", "No description")
            audio_file = os.path.join(scene_folder, "audio.mp3")
            srt_file = os.path.join(scene_folder, "subtitles.srt")

            if not os.path.exists(audio_file):
                edge_tts.generate_audio(
                    text=scene_description,
                    voice=voice,
                    output_file=audio_file,
                    srt_file=srt_file,
                )
            else:
                LOGGER.info(f"Audio file for scene {scene_number} already exists. Skipping generation.")

    def generate_images(self, script_json, folder_path, quantity_each=1):
        image_generator = ImageGenerator()

        for scene_number, scene in enumerate(script_json.get("scenes", []), start=1):
            logger.INFO(f"Processing scene {scene_number}: {scene.get('story_title', 'Untitled')}")
            scene_folder = os.path.join(folder_path, str(scene_number))
            os.makedirs(scene_folder, exist_ok=True)

            image_prompts = scene.get("image_prompts", [])
            for i, prompt in enumerate(image_prompts, start=1):
                for j in range(quantity_each):
                    image_file_path = os.path.join(scene_folder, f"{i}_{j+1}.png")
                    if not os.path.exists(image_file_path):
                        image_data = image_generator.generate_image(theme_prompt=prompt, subfolder=scene_folder, height=576, width=1024, num_inference_steps=2)

                        image_data.save_image(image_file_path)
                    else:
                        LOGGER.info(f"Image {i}_{j+1} for scene {scene_number} already exists. Skipping generation.")

    def run(self):
        data = self.read_json(self.script_path)
        folder_path = self.create_folder(self.script_path)
        self.generate_audio(data, folder_path, self.voice)
        self.generate_images(data, folder_path, quantity_each=self.quantity_each)


if __name__ == "__main__":
    generator = AssetGenerator(project_folder="historic_facts", project_storage="store/projects/", script_path="scripts/top_5_foods_medieval_england.json")
    generator.voice = "en-GB-RyanNeural"
    generator.quantity_each = 3
    generator.run()
