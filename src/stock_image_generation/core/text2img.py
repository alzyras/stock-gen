import torch
from diffusers import FluxPipeline
from pathlib import Path
import os

class ImageGenerator:
    """Class to generate images using the FluxPipeline with optimized VRAM settings."""

    def __init__(self, model_name: str = "black-forest-labs/FLUX.1-schnell", cpu_offload: bool = True, precision: torch.dtype = torch.float16):
        """
        Initializes the image generation pipeline with a specified model and precision.

        Args:
            model_name (str): Name of the pretrained model to load.
            precision (torch.dtype): Precision for the model, defaults to torch.float16.
        """
        self.pipe = FluxPipeline.from_pretrained(model_name, torch_dtype=torch.bfloat16)
        if cpu_offload:
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.vae.enable_slicing()
            self.pipe.vae.enable_tiling()
            self.pipe.to(precision)
    
    def generate_image(self, prompt: str, image_path: Path | str | None,  guidance_scale: float = 0.0, height: int = 1024, width: int = 1024,
                       num_inference_steps: int = 4, max_sequence_length: int = 256) -> None:
        """
        Generates an image based on the given prompt and settings.

        Args:
            prompt (str): Text prompt to guide image generation.
            guidance_scale (float): Guidance scale to adjust adherence to the prompt.
            height (int): Height of the generated image in pixels.
            width (int): Width of the generated image in pixels.
            num_inference_steps (int): Number of steps for inference.
            max_sequence_length (int): Maximum sequence length for the prompt.

        Returns:
            Image: Generated PIL Image.
        """
        result = self.pipe(
            prompt=prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
        ).images[0]    
        result.save(image_path if image_path else os.environ["IMAGE_STORE"])
            



# Example usage:
if __name__ == "__main__":
    generator = ImageGenerator()
    prompt_text = "A beautiful sunset over a calm lake with a small island in the middle."
    image = generator.generate_image(prompt=prompt_text)
    image.show()
    generator.save_image(image, "image.png")
