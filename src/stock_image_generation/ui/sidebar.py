import streamlit as st

from stock_image_generation.ui.functional import load_image_generator

MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
]


def load_sidebar() -> tuple[str, bool, int, int, int, int, str]:
    """Load the sidebar with the necessary widgets."""
    # Set the number of images to generate
    model = st.sidebar.selectbox(
        "Model used for inference:",
        MODELS,
    )
    if st.sidebar.button("Load Model"):
        st.session_state.image_generator = load_image_generator(model)
        st.success("Model loaded successfully!")
    # Set the number of images to generate
    enhance_prompt = st.sidebar.selectbox(
        "Model used for inference:",  # True False, default True
        (False, True),
        index=1,
    )
    images_to_generate = st.sidebar.slider(
        "Number of images to generate:",
        min_value=1,
        max_value=30,
    )
    image_height = st.sidebar.number_input(
        "Image height:",
        min_value=256,
        max_value=4096,
        value=1024,
    )
    image_width = st.sidebar.number_input(
        "Image width:",
        min_value=256,
        max_value=4096,
        value=1024,
    )
    steps = st.sidebar.number_input(
        "Number of inference steps:",
        min_value=1,
        max_value=64,
        value=1,
    )
    image_subfolder = st.sidebar.text_input("Image subfolder (optional):")

    return (
        enhance_prompt,
        images_to_generate,
        image_height,
        image_width,
        steps,
        image_subfolder,
    )
