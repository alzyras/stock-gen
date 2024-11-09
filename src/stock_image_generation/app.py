import streamlit as st

from stock_image_generation.core.text2img import ImageGenerator


@st.cache_resource
def load_image_generator() -> ImageGenerator:
    """Function to load the ImageGenerator object."""
    return ImageGenerator()


def main() -> None:
    """Main function to run the Streamlit app."""
    image_generator = load_image_generator()
    st.title("Image Generation App")
    st.write(
        "Enter a description below, press 'Generate', and see the generated image.",
    )

    # Text input for the user to enter a description
    user_input = st.text_input("Enter description:")

    # Initialize the session state to store the generated image
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None

    # Generate image when the button is pressed
    if st.button("Generate Image"):
        if user_input:
            st.session_state.generated_image = image_generator.generate_image(
                user_input,
            )
            st.success("Image generated successfully!")
    else:
        st.warning("Please enter a description to generate an image.")

    # Display the generated image
    if st.session_state.generated_image:
        st.image(
            st.session_state.generated_image.load_image(),
            caption="Generated Image",
            use_column_width=True,
        )


if __name__ == "__main__":
    main()
