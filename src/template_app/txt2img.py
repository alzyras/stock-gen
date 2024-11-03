from diffusers import DiffusionPipeline
import logging
import os


class ImageGenerator:
    def __init__(self, device="mps", save_folder="store/generated_images/"):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.device = device
        self.save_folder = save_folder

        try:
            self.logger.info("Loading the diffusion pipeline...")
            self.pipe = DiffusionPipeline.from_pretrained("SG161222/RealVisXL_V5.0")
            self.pipe = self.pipe.to(self.device)
            self.logger.info("Pipeline loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading pipeline: {e}")
            raise

        # Recommended if your computer has < 64 GB of RAM
        self.pipe.enable_attention_slicing()

    def generate_image(
        self, 
        prompt: str, 
        negative_prompt: str, 
        height: int = 720, 
        width: int = 1280, 
        steps: int = 25, 
        seed: int = -1, 
        filename: str = "generated_image.png", 
        folder: str = None, 
        project_folder: str = None
    ):
        self.logger.info(f"Prompt: '{prompt}'")
        self.logger.info(f"Resolution: {width}x{height}")
        self.logger.info(f"Steps: {steps}")
        self.logger.info(f"Seed: {seed}")

        # Determine the save path
        if project_folder:
            if folder:
                save_path = f"{self.save_folder}/{project_folder}/{folder}/"
            else:
                save_path = f"{self.save_folder}/{project_folder}/"
        else:
            if folder:
                save_path = f"{self.save_folder}/{folder}/"
            else:
                save_path = self.save_folder

        # Ensure the save path exists
        os.makedirs(save_path, exist_ok=True)

        try:
            self.logger.info(f"Generating image with prompt: '{prompt}'")
            image = self.pipe(prompt,
                              negative_prompt=negative_prompt,
                              num_inference_steps=steps,
                              width=width,
                              height=height,
                              seed=seed
                              ).images[0]
            image.save(f"{save_path}{filename}")
            self.logger.info("Image saved to %s%s", save_path, filename)
        except Exception as e:
            self.logger.exception("Error generating or saving image: %s", e)
            raise


if __name__ == "__main__":
    generator = ImageGenerator()
    generator.generate_image(
        prompt="A beautiful landscape with mountains and a river",
        negative_prompt="",
        height=720,
        width=1280,
        steps=25,
        seed=42,
        filename="test_image.png"
    )
