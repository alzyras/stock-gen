from src.template_app.txt2img import ImageGenerator  # Assuming the class is named ImageGenerator
from src.template_app.llm_stock import AdobeGenerator
import json
import uuid
import os
import random
import glob

root_path = "store/generated_images/"
NUM_PICTURES = 50

def main() -> None:
    """
    Main function to set up parameters and generate images using ImageGenerator.
    """
    # Set up parameters
    steps = 35
    seed = -1
    project_folder = "adobe_stock"
    # Select a random JSON file from the directory
    json_directory = "store/adobe_home_json/"
    subfolders_to_use = ["food", "home_decor","holiday"]  # Set this list to specify which subfolders to use, e.g., ["subfolder1", "subfolder2"]

    if subfolders_to_use:
        json_files = []
        for subfolder in subfolders_to_use:
            json_files.extend(glob.glob(os.path.join(json_directory, subfolder, '*.json')))
    else:
        json_files = glob.glob(os.path.join(json_directory, '**', '*.json'), recursive=True)

    # Create an instance of the image generator
    generator = ImageGenerator()

    for _ in range(NUM_PICTURES):
        selected_json_file = random.choice(json_files)
        print(f'Chosen {selected_json_file} file')

        # Determine the subfolder and load metadata.json
        subfolder = os.path.basename(os.path.dirname(selected_json_file))
        metadata_file = os.path.join(json_directory, subfolder, 'metadata.json')
        print(metadata_file)
        with open(metadata_file, 'r') as file:
            metadata = json.load(file)
        
        category = metadata.get("category", "unknown")
        negative_prompt = metadata.get("negative_prompt", "")
        width = metadata.get("width", 1024)  # Default to 1024 if not specified
        height = metadata.get("height", 1024)  # Default to 1024 if not specified

        # Load the selected JSON file if it's not metadata.json
        if os.path.basename(selected_json_file) != 'metadata.json':
            with open(selected_json_file, 'r') as file:
                json_data1 = json.load(file)
        else:
            print("Selected file is metadata.json, skipping...")
            continue

        # Select a random element from the JSON list
        item = random.choice(json_data1)

        # Generate a unique filename
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}.png"
        json_filename = f"{unique_id}.json"
        prompt = item["description"] + " " + " ".join(item["tags"])
        # Generate the image
        generator.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seed=seed,
            steps=steps,
            filename=filename,
            project_folder=project_folder,
        )

        # Add top level "category" to the JSON metadata
        # Randomize the sequence of tags
        random.shuffle(item["tags"])

        item_with_category = {
            "category": category,
            **item
        }
        
        # Save the JSON metadata
        with open(f"{root_path}{project_folder}/{json_filename}", 'w') as json_file:
            json.dump(item_with_category, json_file, indent=4)

if __name__ == "__main__":
    main()
