from typing import Any

import streamlit as st

from stock_image_generation.core.text2img import ImageData
from stock_image_generation.ui.functional import save_image_helper


def display_images_in_grid(
    images: list[ImageData],
) -> None:  # TODO(Marius): add a way to change the number of columns
    """Display images in a grid with rows of 3 images each."""
    num_rows = (len(images) + 2) // 3

    for row in range(num_rows):
        cols = st.columns(3)
        for col_idx in range(3):
            idx = row * 3 + col_idx
            if idx < len(images):
                display_image_in_column(cols[col_idx], images[idx], idx)


def display_image_in_column(column: Any, image: ImageData, idx: int) -> None:
    """Display a single image in the given column."""
    with column:
        st.image(image.image, use_container_width=True)
        st.markdown(f"**{image.title}**  \n{image.description[:100]}...")
        st.button(
            "Save Image",
            key=f"save_button_{idx}",
            on_click=save_image_helper,
            args=(image,),
        )
