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


def save_image_helper(image_data: ImageData, identifier_helper: int) -> None:
    image_data.save_image()
    image_data.get_categories(st.session_state.image_generator.llm_client)
    with Path(f"{image_data.path}/{image_data.identifier}.json").open("w") as f:
        f.write(image_data.model_dump_json(exclude={"image"}))
    st.success(f"Image {identifier_helper} saved successfully!")


def main() -> None:
    """Main function to run the Streamlit app to display generated images in a grid."""
    st.title("Image Generation App")
    st.write(
        "Enter a description below, press 'Generate Images', and view the generated images.",
    )

    # Text input for the user to enter a description
    user_input = st.text_input("Enter description:")

    # Initialize session state for generated images and number of images to generate
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []
    if "images_to_generate" not in st.session_state:
        st.session_state.images_to_generate = 3  # Default to generating 9 images

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

    # Generate images when the button is pressed
    if st.button("Generate Images"):
        if user_input:
            st.session_state.generated_images = [
                st.session_state.image_generator.generate_image(
                    user_input,
                    height=image_height,
                    width=image_width,
                    num_inference_steps=steps,
                    subfolder=image_subfolder,
                    enhance_prompt=enhance_prompt,
                )
                for _ in range(images_to_generate)
            ]
            st.success("Images generated successfully!")
        else:
            st.warning("Please enter a description to generate images.")

    # Display images in rows of 3
    if st.session_state.generated_images:
        # Calculate number of rows based on the number of images
        num_rows = (
            len(st.session_state.generated_images) + 2
        ) // 3  # Rounding up to ensure full row

        for row in range(num_rows):
            # Create columns for the row
            cols = st.columns(3)
            for col_idx in range(3):
                idx = row * 3 + col_idx
                if idx < len(st.session_state.generated_images):
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
                            args=(
                                current_image,
                                f"{current_image.description[:20]}...",
                            ),
                        )


if __name__ == "__main__":
    main()
