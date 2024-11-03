from src.template_app.txt2img import ImageGenerator  # Assuming the class is named ImageGenerator


def main() -> None:
    """
    Main function to set up parameters and generate an image using ImageGenerator.
    """
    # Set up parameters
    prompt = "a photo of an astronaut riding a fat horse on mars"
    negative_prompt = None
    width = 1280
    height = 720
    seed = -1
    steps = 1
    filename = "astronaut_rides_horse.png"
    project_folder = "soviet_lithuania"

    # Create an instance of the image generator
    generator = ImageGenerator()

    # Generate the image
    generator.generate_image(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        seed=seed,
        steps=steps,
        filename=filename,
        project_folder=project_folder,
    )


if __name__ == "__main__":
    main()