import openai
import json

class AdobeGenerator:
    def __init__(self, api_base="http://localhost:4891/v1", api_key="not needed for a local LLM", model="gpt-4"):
        self.api_base = api_base
        self.api_key = api_key
        self.model = model
        openai.api_base = self.api_base
        openai.api_key = self.api_key

    def generate_json(self, additional_text=""):
        prompt = """
        Please create JSON-formatted prompts for a stock photo website focused on home decor, specifically for living room arrangements. The images should explore a range of living room styles and themes with intricate detailing. Make each JSON prompt a unique decor concept covering styles like minimalist, bohemian, rustic, modern, luxury, and coastal, including variations in lighting, color schemes, and furniture layouts. Each JSON object should include the following fields:

        title: A short, evocative title describing the overall theme or mood of the decor setting.
        description: An elaborate description detailing the decor style, colors, room layout, types of furniture, decorative objects (like vases, coffee tables, wall art), and the ambiance created by lighting and textures.
        tags: A varied and detailed list of at least 30 unique tags for each prompt, tailored to decor elements, room style, color tones, lighting types, and furniture materials. The tags should be different for each prompt, with niche terms related to decor trends and styling elements.

        Output five JSON objects in a list format. Make each description and tag set highly detailed and imaginative for different decor styles. Make sure the JSON output is valid.
        Please output only json, do not output anything else. It has to be valid json.
        Example JSON output:

        [
            {
                "title": "Cozy Minimalist Retreat",
                "description": "A serene minimalist living room that emphasizes simplicity and calm through a neutral color palette. The room features a sleek, low-profile coffee table in matte black, centered on a plush, off-white area rug. Few decorative elements include a set of ceramic vases in beige and white hues, adding a subtle touch of style. The walls are adorned with minimalistic, white frames holding black-and-white photographs of nature scenes, creating a peaceful ambiance. Natural light streams through a large, unobstructed window, further enhancing the sense of openness in the space.",
                "tags": [
                    "minimalist decor", "neutral colors", "sleek design", "modern simplicity", "white frames", 
                    "black-and-white photography", "ceramic vases", "matte finishes", "natural light", 
                    "soft textures", "open floor plan", "airy ambiance", "contemporary style", "subtle elegance", 
                    "cozy yet spacious", "bright atmosphere", "zen-inspired", "clutter-free space", 
                    "neutral rug", "earth tones", "modern furniture", "clean lines", "relaxing space", 
                    "low-profile coffee table", "soothing color scheme", "calm environment", "light-filled room", 
                    "understated elegance", "bare essentials", "uncluttered design", "serene setting"
                ]
            },
            {
                "title": "Vibrant Boho Oasis",
                "description": "A lively, bohemian-inspired living room with vibrant colors and an eclectic mix of decorative objects. The space features a richly colored area rug, woven baskets, and macrame wall hangings. Vintage vases in various shapes and sizes are arranged on a rustic wooden coffee table. The walls are painted a warm terracotta, adding depth to the room, while soft, dimmed lighting provides a cozy and inviting feel. Plants in woven baskets and colorful throw pillows complete the bohemian vibe.",
                "tags": [
                    "bohemian decor", "vibrant colors", "eclectic style", "vintage decor", "colorful rug", 
                    "woven baskets", "macrame wall hanging", "rustic wood", "terracotta walls", "dimmed lighting", 
                    "indoor plants", "earthy tones", "layered textures", "handmade objects", "artisanal look", 
                    "boho chic", "global influence", "warm color scheme", "cozy vibe", "natural materials", 
                    "plush seating", "colorful accents", "hippie-inspired", "textile art", "bold design", 
                    "comfortable atmosphere", "boho lifestyle", "vintage-inspired", "homey feel", 
                    "patterned fabrics", "artsy elements"
                ]
            }
        ]
        """ + additional_text

        response = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=7500,
            temperature=0.28,
            top_p=0.95,
            n=1,
            echo=False,
            stream=False
        )
        # Convert the response text to JSON
        print(response['choices'][0]['text'])
        response_json = json.loads(response['choices'][0]['text'])

        modified_response_text = json.dumps(response_json, indent=4)

        return modified_response_text

# Example usage:
if __name__ == "__main__":
    generator = LLMGenerator()
    result = generator.generate_json("home decor elements", 5)
    print(result)
