import streamlit as st

from stock_image_generation.ui.display_images import display_images_in_grid
from stock_image_generation.ui.generate_images import generate_images
from stock_image_generation.ui.sidebar import load_sidebar


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

    (
        enhance_prompt,
        images_to_generate,
        image_height,
        image_width,
        steps,
        image_subfolder,
    ) = load_sidebar()

    if st.button("Generate Images"):
        generate_images(
            user_input,
            image_height,
            image_width,
            steps,
            image_subfolder,
            enhance_prompt,
            images_to_generate,
        )
    if st.session_state.generated_images:
        display_images_in_grid(st.session_state.generated_images)


if __name__ == "__main__":
    main()
