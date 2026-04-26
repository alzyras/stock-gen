from pathlib import Path

import streamlit as st

from prompt_to_video.core.image import ImageData, ImageGenerator

MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
]


@st.cache_resource
def load_image_generator(model_name: str) -> ImageGenerator:
    """Load and cache the image generator."""
    return ImageGenerator(model_name)


def save_image_helper(image_data: ImageData, identifier_helper: str) -> None:
    """Persist the image and its sidecar metadata."""
    image_path = image_data.save_image()
    image_data.get_categories(st.session_state.image_generator.llm_client)
    metadata_path = Path(image_data.path) / f"{image_data.identifier}.json"
    metadata_path.write_text(
        image_data.model_dump_json(exclude={"image"}),
        encoding="utf-8",
    )
    st.success(f"Image {identifier_helper} saved to {image_path}")


def main() -> None:
    """Run the Streamlit image generation app."""
    st.title("Image Generation App")
    st.write("Enter a description, generate images, then save selected results.")

    user_input = st.text_input("Enter description:")

    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []
    if "image_generator" not in st.session_state:
        st.session_state.image_generator = None

    model = st.sidebar.selectbox("Model used for inference:", MODELS)
    if st.sidebar.button("Load Model"):
        st.session_state.image_generator = load_image_generator(model)
        st.success("Model loaded successfully")

    images_to_generate = st.sidebar.slider(
        "Number of images to generate:",
        min_value=1,
        max_value=30,
        value=3,
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

    if st.button("Generate Images"):
        if not user_input:
            st.warning("Please enter a description to generate images.")
        elif st.session_state.image_generator is None:
            st.warning("Load a model before generating images.")
        else:
            st.session_state.generated_images = [
                st.session_state.image_generator.generate_image(
                    user_input,
                    height=image_height,
                    width=image_width,
                    num_inference_steps=steps,
                    subfolder=image_subfolder or None,
                )
                for _ in range(images_to_generate)
            ]
            st.success("Images generated successfully")

    if st.session_state.generated_images:
        num_rows = (len(st.session_state.generated_images) + 2) // 3
        for row in range(num_rows):
            cols = st.columns(3)
            for col_idx in range(3):
                idx = row * 3 + col_idx
                if idx >= len(st.session_state.generated_images):
                    continue
                current_image = st.session_state.generated_images[idx]
                with cols[col_idx]:
                    st.image(current_image.image, use_container_width=True)
                    st.markdown(
                        f"**{current_image.title}**  \n{current_image.description[:200]}",
                    )
                    st.button(
                        "Save Image",
                        key=f"save_button_{idx}",
                        on_click=save_image_helper,
                        args=(current_image, f"{current_image.description[:20]}..."),
                    )


if __name__ == "__main__":
    main()
