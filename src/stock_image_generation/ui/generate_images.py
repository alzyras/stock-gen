import streamlit as st


def generate_images(
    user_input: str,
    image_height: int,
    image_width: int,
    steps: int,
    image_subfolder: str,
    enhance_prompt: bool,
    images_to_generate: int,
) -> None:
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
