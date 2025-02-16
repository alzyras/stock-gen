import torch
from diffusers import FluxPipeline
from PIL.Image import Image

from prompt_to_video.settings import IMAGE_GENERATION_MODEL, USE_MPS


class ImageGenerator:
    """Class to generate images using the FluxPipeline with optimized VRAM settings."""

    def __init__(
        self,
        model_name: str = IMAGE_GENERATION_MODEL,
        cpu_offload: bool = False,
        precision: torch.dtype = torch.float16,
        use_mps: bool = USE_MPS,
    ) -> None:
        """Initializes the image generation with a specified model.

        Args:
            model_name (str): Name of the pretrained model to load.
            cpu_offload (bool): Flag to enable CPU offloading for the model.
            precision (torch.dtype): Precision for the model, defaults to torch.float16.
            use_mps (bool): Flag to enable Mixed Precision Scoring (MPS) for the model.
        """
        if use_mps:
            self.pipe = FluxPipeline.from_pretrained(
                model_name, torch_dtype=torch.bfloat16
            ).to("mps")
        else:
            self.pipe = FluxPipeline.from_pretrained(
                model_name, torch_dtype=torch.bfloat16
            )
        if cpu_offload:
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.vae.enable_slicing()
            self.pipe.vae.enable_tiling()
            self.pipe.to(precision)

    def generate_image(
        self,
        prompt: str,
        guidance_scale: float = 0.0,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 1,
        max_sequence_length: int = 256,
    ) -> Image:
        """Generates and saves an image based on the given prompt and settings.

        Args:
            prompt (str): Text prompt to guide image generation.
            subfolder (str): Subfolder to save the generated image.
            guidance_scale (float): Guidance scale to adjust adherence to the prompt.
            height (int): Height of the generated image in pixels.
            width (int): Width of the generated image in pixels.
            num_inference_steps (int): Number of steps for inference.
            max_sequence_length (int): Maximum sequence length for the prompt.

        Returns:
            PictureData: Object containing the generated image metadata.
        """
        return self.pipe(
            prompt=prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
        ).images[0]
