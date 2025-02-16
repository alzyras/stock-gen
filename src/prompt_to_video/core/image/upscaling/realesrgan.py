import logging
import subprocess
from pathlib import Path

from prompt_to_video.core.image.upscaling import ImageUpscaler

LOGGER = logging.getLogger(__name__)


class RealesrganUpscaler(ImageUpscaler):
    def __init__(self) -> None:
        """Initializes the Upscaler class.

        Currently, this constructor does not perform any operations.
        """

    def upscale_image(
        self,
        input_path: str | Path,
        save_path: str | Path,
        prompt: str = "",
    ) -> bool:
        """Upscale a low-resolution image using Real-ESRGAN.

        Args:
            input_path (str | Path): The path to the low-res input image.
            save_path (str | Path): The path to save the upscaled image.
            prompt (str): The textual description to guide the upscaling.
                Defaults to an empty string.

        Returns:
            bool: True if the image was successfully upscaled, False otherwise.
        """
        upscale_factor = 4
        LOGGER.info(f"Prompt not used: {prompt}")
        model = "realesrgan-x4plus"
        model_path = "hf_cache/realesrgan-models/"
        LOGGER.info("Upscaling %s to %s using Real-ESRGAN.", input_path, save_path)
        # Enhance image using Real-ESRGAN
        enhance_command = [
            "./hf_cache/realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan",
            "-i",
            input_path,
            "-o",
            save_path,
            "-n",
            model,
            "-m",
            model_path,
            "-s",
            str(upscale_factor),
            "-f",
            "jpg",
        ]

        try:
            # Sanitize input to prevent execution of untrusted input
            # Sanitize input to prevent execution of untrusted input
            sanitized_command = [str(arg) for arg in enhance_command]

            # Ensure the command is safe by avoiding shell=True
            result = subprocess.run(  # noqa: S603 RUF100
                sanitized_command,
                check=True,
                capture_output=True,
                text=True,
                shell=False,
            )
            LOGGER.info("Enhancing %s to %s", input_path, save_path)
            LOGGER.info(result.stdout)
            LOGGER.error(result.stderr)
            LOGGER.info("Upscaled %s and saved to %s", input_path, save_path)
            return True  # noqa: TRY300
        except subprocess.CalledProcessError:
            LOGGER.exception(
                "Error during image enhancement for %s",
                input_path,
            )
            return False
