from pathlib import Path

import streamlit as st

from stock_image_generation.core.text2img import ImageData, ImageGenerator

MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
]


@st.cache_resource
def load_image_generator(model_name: str) -> ImageGenerator:
    """Function to load the ImageGenerator object."""
    return ImageGenerator(model_name)


def save_image_helper(image_data: ImageData) -> None:
    image_data.save_image()
    image_data.get_categories(st.session_state.image_generator.llm_client)
    with Path(f"{image_data.path}/{image_data.identifier}.json").open("w") as f:
        f.write(image_data.model_dump_json(exclude={"image"}))
    st.success(f"Image {image_data.title} saved successfully!")
