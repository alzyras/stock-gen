from src.template_app.txt2img import ImageGenerator  # Assuming the class is named ImageGenerator
from src.template_app.llm_stock import AdobeGenerator
import json
import uuid
import os
import random

root_path = "store/generated_images/"

json_data = """

"""
json_data = """

"""






def main() -> None:
    """
    Main function to set up parameters and generate an image using ImageGenerator.
    """
    # Set up parameters
    prompt = "a photo of an astronaut riding a fat horse on mars"
    negative_prompt = "distorted furniture proportions, warped furniture shapes, unrealistic textures, inconsistent lighting, poor object alignment, blurry details, jagged edges on furniture, missing or floating objects, excessive noise, pixelated surfaces, unnatural colors, low resolution, incorrect shadows, artificial reflections, exaggerated colors, mismatched decor styles, awkward object scaling, stretched walls, grainy fabrics, cluttered or messy compositions, stiff cushions, poorly rendered wood grain, plastic-looking textures, incorrect perspective, cartoonish elements, overexposed lighting, over-saturated colors, inconsistent color tones, missing details, warped rugs, unnatural plants, artificial shadows, blurry art frames, unrealistic reflections on surfaces, misaligned wall art, incorrect furniture angles, overly bright spots, faded or washed-out colors, distorted windows, poorly blended lighting, disjointed decor elements, exaggerated reflections, unbalanced layout, empty space imbalance, unintentional duplicates, incorrect object layering, mismatched color palette, off-scale furniture, lifeless fabrics, fake-looking textures, cluttered tables, broken chair legs, floating decor objects, over-polished surfaces, asymmetrical designs, forced perspective, overly sharp edges, muddy colors, jagged shadows, glitchy reflections, incorrect wall angles, warped windows, unnatural spacing, faded elements, cluttered arrangements, artificial glow"
    width = 1280
    height = 720
    seed = -1
    steps = 35
    project_folder = "adobe_stock"
    # Select a random JSON file from the directory
    json_directory = "store/adobe_home_json/"
    json_files = [f for f in os.listdir(json_directory) if f.endswith('.json')]
    selected_json_file = random.choice(json_files)
    print(f'Chosen {selected_json_file} file')
    # Load the selected JSON file
    with open(os.path.join(json_directory, selected_json_file), 'r') as file:
        json_data1 = json.load(file)
    #json_data = json.loads(AdobeGenerator().generate_json())
    # Create an instance of the image generator
    generator = ImageGenerator()

    for item in json_data1:
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

        # Save the JSON metadata
        with open(f"{root_path}{project_folder}/{json_filename}", 'w') as json_file:
            json.dump(item, json_file, indent=4)



if __name__ == "__main__":
    for i in range(5):
        main()