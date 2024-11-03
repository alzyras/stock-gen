from src.template_app.txt2img import ImageGenerator  # Assuming the class is named ImageGenerator
from src.template_app.llm_stock import AdobeGenerator
import json
import uuid
import os
import random

root_path = "store/generated_images/"


json_data = """
[
    {
        "title": "Unicorn Picnic in Enchanted Meadow",
        "description": "A magical unicorn picnic set in an enchanted meadow, featuring shimmering foods like stardust cupcakes, rainbow fruit salads, and crystal-clear spring water. The unicorns gather under a golden oak tree, surrounded by glowing flowers and floating fireflies, sharing laughter and stories.",
        "tags": [
            "unicorns", "enchanted meadow", "magical picnic", 
            "stardust cupcakes", "rainbow fruits", "mythical gathering", 
            "glowing flowers", "golden oak tree", "mythical feast", 
            "fantasy setting", "ethereal beauty", "whimsical vibes", 
            "fairy lights", "mystical creatures", "fantasy adventure", 
            "mythical stories", "unicorn friends", "enchantment"
        ]
    },
    {
        "title": "Dragon Spa Day at the Crystal Springs",
        "description": "A peaceful spa retreat for dragons at the legendary Crystal Springs, where they soak in hot mineral pools and relax under the gentle mist of the waterfall. Surrounded by sparkling amethysts and gentle harp music, dragons unwind and rejuvenate.",
        "tags": [
            "dragon spa", "Crystal Springs", "mineral pools", 
            "relaxing dragons", "waterfall mist", "fantasy relaxation", 
            "sparkling amethysts", "harp music", "dragon wellness", 
            "mythical creatures", "enchanted setting", "rejuvenation", 
            "ethereal beauty", "fantasy retreat", "magic crystals", 
            "spa day", "dragon pampering", "healing springs"
        ]
    },
    {
        "title": "Phoenix Bonfire Celebration",
        "description": "A grand bonfire event where phoenixes gather to celebrate their rebirth cycles. With crackling flames illuminating the night sky, the phoenixes share wisdom, engage in storytelling, and display their fiery feathers, lighting up the magical forest.",
        "tags": [
            "phoenix", "bonfire celebration", "rebirth cycle", 
            "fiery feathers", "mythical wisdom", "storytelling", 
            "magical forest", "phoenix gathering", "mystical flames", 
            "fantasy creatures", "celestial event", "mythical gathering", 
            "forest magic", "eternal cycle", "firelight", 
            "legendary tales", "creature gathering", "fantasy night"
        ]
    },
    {
        "title": "Pegasus Sky Race Over Floating Isles",
        "description": "A thrilling race among Pegasus across the Floating Isles, where each rider competes on their winged horse through clouds, rainbows, and starlit skies. Spectators cheer from atop island cliffs, waving flags and glowing lights in the sky.",
        "tags": [
            "Pegasus race", "Floating Isles", "sky competition", 
            "winged horses", "cloud race", "mythical event", 
            "rainbows", "island cliffs", "glowing lights", 
            "aerial sports", "starlit skies", "fantasy excitement", 
            "flying creatures", "mythical creatures", "spectators", 
            "legendary race", "cheering crowds", "fantasy sky"
        ]
    },
    {
        "title": "Mermaid Gala in Coral Palace",
        "description": "An underwater gala hosted by mermaids in the grand Coral Palace, with bioluminescent plants lighting the hall and enchanting music filling the waters. Creatures from all ocean realms gather for a night of dancing, feasting, and celebrating oceanic beauty.",
        "tags": [
            "mermaid gala", "Coral Palace", "underwater festival", 
            "ocean creatures", "bioluminescent plants", "enchanted music", 
            "ocean beauty", "mythical gathering", "fantasy underwater", 
            "sea creatures", "oceanic celebration", "mermaid dance", 
            "coral decorations", "fantasy feast", "ocean magic", 
            "sea gala", "mythical party", "deep sea elegance"
        ]
    },
    {
        "title": "Mystical Unicorn and Fairy Garden",
        "description": "A peaceful garden where unicorns and fairies coexist among towering flowers and glowing mushrooms. The air is filled with magic, and the creatures interact harmoniously, sharing enchanted stories and feasting on nectar and wild berries.",
        "tags": [
            "unicorn garden", "fairy realm", "glowing mushrooms", 
            "towering flowers", "mythical coexistence", "enchanted stories", 
            "magical feast", "nectar", "fantasy garden", 
            "fairy lights", "mythical creatures", "fantasy scenery", 
            "harmony", "wild berries", "enchanted interaction", 
            "ethereal beauty", "fairy friends", "unicorns"
        ]
    },
    {
        "title": "Griffin Mountain Campfire Feast",
        "description": "A campfire feast hosted by griffins high atop the Mystic Mountains. Under a starry sky, they feast on roasted wild herbs and fruits, sharing tales of adventures and spreading their wings to warm up by the fire.",
        "tags": [
            "griffin feast", "Mystic Mountains", "campfire", 
            "wild herbs", "starry sky", "mythical gathering", 
            "winged creatures", "adventure tales", "mountain gathering", 
            "griffins", "mythical creatures", "fantasy camping", 
            "roasted food", "legendary creatures", "fantasy night", 
            "creature storytelling", "enchanted mountains", "winged feast"
        ]
    },
    {
        "title": "Magical Unicorn Moonlit Parade",
        "description": "An enchanting moonlit parade where unicorns adorned in crystal tiaras and silk capes prance through a forest trail. With fireflies lighting the way and their manes sparkling, they create a mesmerizing display of grace and wonder.",
        "tags": [
            "unicorn parade", "moonlit forest", "crystal tiaras", 
            "silk capes", "magical display", "firefly lights", 
            "sparkling manes", "forest trail", "fantasy procession", 
            "graceful unicorns", "mystical beauty", "night wonder", 
            "enchanted forest", "fantasy creatures", "mythical event", 
            "night magic", "unicorn adornment", "forest beauty"
        ]
    },
    {
        "title": "Enchanted Creature's Tea Party",
        "description": "A whimsical tea party in a fairy glade, attended by unicorns, fairies, and talking animals. Surrounded by tea tables adorned with floral arrangements, they sip herbal teas and enjoy enchanted pastries under dappled sunlight and magic-filled air.",
        "tags": [
            "mythical tea party", "fairy glade", "talking animals", 
            "floral tea tables", "enchanted pastries", "fantasy gathering", 
            "dappled sunlight", "herbal teas", "magical atmosphere", 
            "unicorns", "fairies", "fantasy snacks", 
            "glade beauty", "whimsical setting", "mystical gathering", 
            "mythical creatures", "tea time", "fantasy desserts"
        ]
    }
]
"""

json_data = json.loads(json_data)




def main() -> None:
    """
    Main function to set up parameters and generate an image using ImageGenerator.
    """
    # Set up parameters
    prompt = "a photo of an astronaut riding a fat horse on mars"
    negative_prompt = "distortion, artifacts, blurry, overexposed, underexposed, low contrast, high contrast, grainy, noisy, out of focus, low resolution, over saturated, under saturated, unnatural colors, lens flare, chromatic aberration, vignette, motion blur, pixelated, compression artifacts, unnatural spacing, faded elements, cluttered arrangements, artificial glow"
    width = 1680
    height = 720
    seed = -1
    steps = 25
    project_folder = "adobe_stock"
    # Select a random JSON file from the directory
    # Create an instance of the image generator
    generator = ImageGenerator()

    for item in json_data:
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