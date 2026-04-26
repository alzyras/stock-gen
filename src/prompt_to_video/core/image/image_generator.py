import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch
from diffusers import FluxPipeline
from PIL import Image as PILImage

from prompt_to_video.settings import IMAGE_GENERATION_MODEL, USE_MPS


@dataclass
class ImageData:
    """Generated image plus the metadata needed by the app and asset pipeline."""

    image: PILImage.Image
    prompt: str
    path: str = "data/images"
    identifier: str | None = None
    title: str | None = None
    description: str | None = None
    categories: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.identifier = self.identifier or _prompt_identifier(self.prompt)
        self.title = self.title or self.prompt[:80]
        self.description = self.description or self.prompt

    def save_image(self, path: str | Path | None = None) -> Path:
        """Save the generated image and return the output path."""
        output_path = (
            Path(path)
            if path is not None
            else Path(self.path) / f"{self.identifier}.png"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(output_path)
        return output_path

    def get_categories(self, _llm_client: Any | None = None) -> list[str]:
        """Populate basic categories without requiring an LLM call."""
        if self.categories:
            return self.categories
        words = re.findall(r"[A-Za-z][A-Za-z-]{2,}", self.prompt.lower())
        stop_words = {"and", "the", "for", "with", "from", "into", "that", "this"}
        self.categories = [
            word for word in dict.fromkeys(words) if word not in stop_words
        ][:8]
        return self.categories

    def model_dump_json(self, *, exclude: set[str] | None = None) -> str:
        """Small compatibility shim for the Streamlit app's previous Pydantic model."""
        import json

        excluded = exclude or set()
        data = {
            "prompt": self.prompt,
            "path": self.path,
            "identifier": self.identifier,
            "title": self.title,
            "description": self.description,
            "categories": self.categories,
        }
        return json.dumps(
            {key: value for key, value in data.items() if key not in excluded}
        )


def _prompt_identifier(prompt: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48]
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
    return f"{slug or 'image'}-{digest}"


class ImageGenerator:
    """Generate images using FluxPipeline with a stable application-facing API."""

    def __init__(
        self,
        model_name: str = IMAGE_GENERATION_MODEL,
        cpu_offload: bool = False,
        precision: torch.dtype = torch.float16,
        use_mps: bool = USE_MPS,
    ) -> None:
        self.model_name = model_name
        self.llm_client = None
        device = "mps" if use_mps and torch.backends.mps.is_available() else None
        dtype = torch.float16 if device == "mps" else precision

        self.pipe = FluxPipeline.from_pretrained(model_name, torch_dtype=dtype)
        if cpu_offload:
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.vae.enable_slicing()
            self.pipe.vae.enable_tiling()
        elif device is not None:
            self.pipe = self.pipe.to(device)

    def generate_image(
        self,
        prompt: str | None = None,
        *,
        theme_prompt: str | None = None,
        subfolder: str | Path | None = None,
        guidance_scale: float = 0.0,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 1,
        max_sequence_length: int = 256,
        seed: int | None = None,
    ) -> ImageData:
        """Generate an image and return it with metadata."""
        final_prompt = prompt or theme_prompt
        if not final_prompt:
            msg = "Either prompt or theme_prompt must be provided."
            raise ValueError(msg)

        generator = None
        if seed is not None:
            generator = torch.Generator("cpu").manual_seed(seed)

        image = self.pipe(
            prompt=final_prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
            generator=generator,
        ).images[0]
        return ImageData(
            image=image,
            prompt=final_prompt,
            path=str(subfolder) if subfolder is not None else "data/images",
        )
