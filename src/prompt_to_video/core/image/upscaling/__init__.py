from prompt_to_video.core.image.upscaling.abstract import ImageUpscaler
from prompt_to_video.core.image.upscaling.diffusion_upscaler import DiffusionUpscaler
from prompt_to_video.core.image.upscaling.realesrgan import RealesrganUpscaler
from prompt_to_video.settings import UPSCALER_TYPE

INVALID_UPSCALER_TYPE = "Invalid upscaler type provided."

AVAILABLE_UPSCALERS = {
    "REALESRGAN": RealesrganUpscaler,
    "DIFFUSION": DiffusionUpscaler,
}


def get_upscaler() -> ImageUpscaler:
    return AVAILABLE_UPSCALERS[UPSCALER_TYPE]()


__all__ = ["ImageUpscaler", "get_upscaler"]
