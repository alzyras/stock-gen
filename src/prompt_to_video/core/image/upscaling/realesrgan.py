import logging
import subprocess
from pathlib import Path

from prompt_to_video.core.image.upscaling.abstract import ImageUpscaler
from prompt_to_video.settings import REALESRGAN_BINARY, REALESRGAN_MODEL_PATH

LOGGER = logging.getLogger(__name__)


class RealesrganUpscaler(ImageUpscaler):
    """Upscale images with the Real-ESRGAN NCNN Vulkan binary."""

    def __init__(
        self,
        binary_path: str | Path = REALESRGAN_BINARY,
        model_path: str | Path = REALESRGAN_MODEL_PATH,
        model: str = "realesrgan-x4plus",
        upscale_factor: int = 4,
    ) -> None:
        self.binary_path = Path(binary_path)
        self.model_path = Path(model_path)
        self.model = model
        self.upscale_factor = upscale_factor

    def upscale_image(
        self,
        input_path: str | Path,
        save_path: str | Path,
        prompt: str = "",
    ) -> bool:
        """Upscale a low-resolution image using Real-ESRGAN."""
        if prompt:
            LOGGER.info("Real-ESRGAN does not use text prompts; ignoring prompt.")
        if not self.binary_path.exists():
            LOGGER.error("Real-ESRGAN binary not found: %s", self.binary_path)
            return False

        save = Path(save_path)
        save.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(self.binary_path),
            "-i",
            str(input_path),
            "-o",
            str(save),
            "-n",
            self.model,
            "-m",
            str(self.model_path),
            "-s",
            str(self.upscale_factor),
            "-f",
            save.suffix.lstrip(".") or "jpg",
        ]

        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                shell=False,
            )
        except subprocess.CalledProcessError:
            LOGGER.exception("Error during image enhancement for %s", input_path)
            return False

        if result.stdout:
            LOGGER.info(result.stdout)
        if result.stderr:
            LOGGER.warning(result.stderr)
        LOGGER.info("Upscaled %s and saved to %s", input_path, save)
        return True
