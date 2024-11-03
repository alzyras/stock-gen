from src.template_app.llm import LLMGenerator  # Assuming the class is named ImageGenerator
from src.template_app.txt2img import ImageGenerator
import uuid
import logging
import json as json_lib
import time
import os
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

HOW_MANY_PER_PIC = 4
# Ask for the project folder
project_folder = input("Enter the project folder: ").strip()
metadata_filename = f"store/generated_images/{project_folder}/metadata.json"
csv_filename = f"store/generated_images/{project_folder}/metadata.csv"
prompt_prefix = "photorealistic "

# Check if metadata.json exists
if os.path.exists(metadata_filename):
    LOGGER.info(f"{metadata_filename} exists. Reading from it.")
    with open(metadata_filename, 'r') as metadata_file:
        json_data = json_lib.load(metadata_file)
else:
    LOGGER.error(f"{metadata_filename} does not exist. Exiting.")
    exit(1)

existing_images = []
if os.path.exists(csv_filename):
    with open(csv_filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            existing_images.append((int(row[0]), int(row[3])))  # (scene_number, index)
print(existing_images)
# Start timing the entire process
start_time_total = time.time()

for scene in json_data['notable_moments']:
    start_time_scene = time.time()
    LOGGER.info(f"Processing scene: {scene['scene_description']}")
    print(scene['scene_description'])
    print()
    scene_number = scene['scene_number']
    negative_prompt = "distorted faces, distorted eyes, blurry, distortion, artifacts, noise, abstract, surreal, psychedelic, dreamlike"
    height = 720
    width = 1280
    seed = -1
    steps = 25
    generator = ImageGenerator()
    for prompt_index, prompt in enumerate(scene['image_prompts']):
        for i in range(HOW_MANY_PER_PIC):
            LOGGER.info(f"Current image and scene: {(scene_number, prompt_index, i)}")
            if (scene_number, prompt_index, i) in existing_images:
                LOGGER.info(f"Image {i+1}/{HOW_MANY_PER_PIC} for scene {scene_number}, prompt {prompt_index} already exists. Skipping.")
                continue
            filename = f"{prompt_index}_{uuid.uuid4()}.png"
            LOGGER.info(f"Generating image {i+1}/{HOW_MANY_PER_PIC} for scene {scene_number}, prompt {prompt_index} with filename {filename}")
            generator.generate_image(
                prompt=prompt_prefix + prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                steps=steps,
                filename=filename,
                folder=scene_number,
                project_folder=project_folder,
            )
            # Write to CSV
            with open(csv_filename, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([scene_number, prompt, filename, prompt_index, i])
            existing_images.append((scene_number, prompt_index, i))
    end_time_scene = time.time()
    LOGGER.info(f"Time taken to generate scene {scene_number}: {end_time_scene - start_time_scene:.2f} seconds")

# End timing the entire process
end_time_total = time.time()
# Create a 'complete' file in the project folder
complete_file_path = f"store/generated_images/{project_folder}/complete"
with open(complete_file_path, 'w') as complete_file:
    complete_file.write("Image generation complete.")
LOGGER.info(f"Created 'complete' file at {complete_file_path}")
LOGGER.info(f"Total time taken to generate all scenes: {end_time_total - start_time_total:.2f} seconds")
