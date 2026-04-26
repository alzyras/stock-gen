from prompt_to_video.core.image.upscaling.abstract import ImageUpscaler
from prompt_to_video.core.image.upscaling.diffusion_upscaler import DiffusionUpscaler
from prompt_to_video.core.image.upscaling.realesrgan import RealesrganUpscaler
from prompt_to_video.settings import UPSCALER_TYPE

AVAILABLE_UPSCALERS = {
    "REALESRGAN": RealesrganUpscaler,
    "DIFFUSION": DiffusionUpscaler,
}


def get_upscaler(upscaler_type: str = UPSCALER_TYPE) -> ImageUpscaler:
    """Build the configured image upscaler."""
    normalized_type = upscaler_type.upper()
    try:
        return AVAILABLE_UPSCALERS[normalized_type]()
    except KeyError as exc:
        available = ", ".join(sorted(AVAILABLE_UPSCALERS))
        msg = f"Invalid upscaler type {upscaler_type!r}. Choose one of: {available}."
        raise ValueError(msg) from exc


__all__ = ["DiffusionUpscaler", "ImageUpscaler", "RealesrganUpscaler", "get_upscaler"]
