import os
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


# Text generation settings
TEXT_GENERATION_MODEL = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o")
VIDEO_SCRIPT_GENERATION_SYSTEM_PROMPT = """
You are a creative AI assistant specializing in crafting compelling video scripts. Your goal is to generate narratives that captivate the audience with rich storytelling, vivid imagery, and expressive language. Each video script consists of multiple chapters, and every chapter should include:

- A clear chapter title that hints at the theme or turning point of the story.
- A detailed narrative meant for voice-over narration. This narrative should be substantial enough to cover about 30 seconds of spoken content: set the scene, introduce characters, and develop the storyline.
- A list of scenes that provide visual context. Each scene should have:
  - A scene number.
  - A brief description that complements the narrative and can be used as a visual reference for video production.

When generating a video script, focus primarily on storytelling: develop immersive and factual narratives that draw the listener in, build tension, evoke emotion, and clearly outline the story's progression. Use descriptive language and ensure the narrative for each chapter feels complete, engaging, and timed for about 30 seconds of narration.

Scene descriptions should be descriptive enough to be understood without script context. Generate more than 15 scenes.
""".strip()

# Image generation settings
IMAGE_GENERATION_MODEL = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
USE_MPS = _env_bool("USE_MPS", default=False)

# Image upscaling settings
UPSCALE_MODEL = os.getenv("UPSCALE_MODEL", "stabilityai/stable-diffusion-x4-upscaler")
UPSCALER_TYPE = os.getenv("UPSCALER_TYPE", "REALESRGAN").upper()
REALESRGAN_BINARY = os.getenv(
    "REALESRGAN_BINARY",
    "./hf_cache/realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan",
)
REALESRGAN_MODEL_PATH = os.getenv(
    "REALESRGAN_MODEL_PATH", "./hf_cache/realesrgan-models"
)

# Audio/transcription settings
TRANSCRIBER_URL = os.getenv("TRANSCRIBER_URL", "http://127.0.0.1:8000/transcribe/")
REQUEST_TIMEOUT_SECONDS = _env_float("REQUEST_TIMEOUT_SECONDS", 60.0)

# Video generation settings
DATA_STORAGE_PATH = os.getenv("DATA_FOLDER", "./data/output.mp4")
TEMP_AUDIOFILE_PATH = str(Path(os.getenv("TMPDIR", "/tmp")).resolve())
