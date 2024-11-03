import openai
import json

class LLMGenerator:
    def __init__(self, api_base="http://localhost:4891/v1", api_key="not needed for a local LLM", model="gpt-4"):
        self.api_base = api_base
        self.api_key = api_key
        self.model = model
        openai.api_base = self.api_base
        openai.api_key = self.api_key

    def generate_json(self, civilization, time_period, scene_number, scene_type, additional_notes=""):
        prompt = """
        Generate a JSON object for a civilization/country {civilization} during the time period {time_period}. The JSON should include the following structure (create {scene_number} {scene_type}):

        {{
            "civilization": "{civilization}",
            "time_period": "{time_period}",
            "notable_moments": [
                {{
                    "scene_number": Z,
                    "scene_description": "A brief text description suitable for text-to-speech explaining the historical significance of this scene. Make it at least two sentences long.",
                    "image_prompts": [
                        "A 4k, photorealistic image of [detailed description of the scene], accurately depicting the historical context and elements.",
                        "A 4k, photorealistic image of [another detailed description of the scene], accurately depicting the historical context and elements.",
                        "A 4k, photorealistic image of [another detailed description of the scene], accurately depicting the historical context and elements.",
                        "A 4k, photorealistic image of [another detailed description of the scene], accurately depicting the historical context and elements."
                    ]
                }},
                ...
            ]
        }}

        Please ensure that:
        - X is the name of the civilization, country, place.
        - Y is the specific time period you are focusing on.
        - Z is the number of scenes you want to generate (e.g., 5).
        - Each scene includes a historically accurate description and four prompts for image generation, ensuring the descriptions are vivid and contextual.

        Please ensure that the scenes are directly related to the specified civilization and time period, with historically accurate descriptions and prompts for image generation. Do not change the civilizations.

        In final result give the json only. don't say here is the json object or anything, please just give the json object. Make the image prompts always have 4k, photorealistic, historically accurate etc. in prompts.
        Make image prompts more elaborate and have specific people doing specific things or specific objects.
        Make sure in each image prompt the images are colored, detailed, and historically accurate. Please indicate in every photo prompt that the image has to be colored, 4k, photorealistic, and historically accurate.
        {additional_notes}
        """.format(
            civilization=civilization,
            time_period=time_period,
            scene_number=scene_number,
            scene_type=scene_type,
            additional_notes=additional_notes
        )

        response = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=20000,
            temperature=0.28,
            top_p=0.95,
            n=1,
            echo=False,
            stream=False
        )
        # Convert the response text to JSON
        response_json = json.loads(response['choices'][0]['text'])

        # Modify the image prompts
        for notable_moment in response_json['notable_moments']:
            for i in range(len(notable_moment['image_prompts'])):
                notable_moment['image_prompts'][i] += f" ({civilization}, {time_period}, in color)"

        # Convert the modified JSON back to a string
        modified_response_text = json.dumps(response_json, indent=4)


        return modified_response_text

# Example usage:
if __name__ == "__main__":
    generator = LLMGenerator()
    result = generator.generate_json("Ancient Rome", "500 BC", 5, "notable moments")
    print(result)
