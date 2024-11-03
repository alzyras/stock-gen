from src.template_app.llm import LLMGenerator  # Assuming the class is named ImageGenerator
from src.template_app.txt2img import ImageGenerator
import uuid
import logging
import json as json_lib
import time
import os

generator = LLMGenerator()

civilization = "USA"
time_period = "2070s"
scene_number = 10
scene_type = "major aspects of daily life"
additional_notes = ""
generation_number = 4

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Define the project folder and metadata filename
project_folder = (civilization + "_" + time_period).replace(" ", "_")
metadata_filename = f"store/generated_images/{project_folder}/metadata.json"
project_root = "store/generated_images/"

# Check if metadata.json exists
if os.path.exists(metadata_filename):
    LOGGER.info(f"{metadata_filename} exists. Reading from it.")
    with open(metadata_filename, 'r') as metadata_file:
        json_data = json_lib.load(metadata_file)
else:
    LOGGER.info(f"{metadata_filename} does not exist. Generating new metadata.")
    while True:
        json = generator.generate_json(civilization, time_period, scene_number, scene_type, additional_notes=additional_notes)
        json_data = json_lib.loads(json)
        print(json_lib.dumps(json_data, indent=4))
        user_input = input("Is this JSON good? (yes/no): ").strip().lower()
        if user_input == 'yes':
            break
        LOGGER.info("Regenerating JSON...")

    # Save the JSON as metadata.json to the project folder
    os.makedirs(project_root + project_folder, exist_ok=True)
    with open(metadata_filename, 'w') as metadata_file:
        json_lib.dump(json_data, metadata_file, indent=4)

# Start timing the entire process
start_time_total = time.time()

for scene in json_data['notable_moments']:
    start_time_scene = time.time()
    LOGGER.info(f"Processing scene: {scene['scene_description']}")
    print(scene['scene_description'])
    #print(scene['image_prompts'])
    print()
    scene_number = scene['scene_number']
    prompt = scene['image_prompts']
    negative_prompt = "distorted faces, distorted eyes, blurry, distortion, artifacts, noise, abstract, surreal, psychedelic, dreamlike"
    height = 720
    width = 1280
    seed = -1
    steps = 25
    project_folder = (civilization + "_" + time_period).replace(" ", "_")
    generator = ImageGenerator()
    for prompt_index, prompt in enumerate(scene['image_prompts'], start=1):
        for i in range(generation_number):
            filename = f"{prompt_index}_{uuid.uuid4()}.png"
            LOGGER.info(f"Generating image {i+1}/4 for scene {scene_number} with filename {filename}")
            generator.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                steps=steps,
                filename=filename,
                folder=scene_number,
                project_folder=project_folder,
            )
    end_time_scene = time.time()
    LOGGER.info(f"Time taken to generate scene {scene_number}: {end_time_scene - start_time_scene:.2f} seconds")

# End timing the entire process
end_time_total = time.time()
LOGGER.info(f"Total time taken to generate all scenes: {end_time_total - start_time_total:.2f} seconds")