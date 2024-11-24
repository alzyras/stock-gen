# Project Documentation

This documentation lists the classes, functions, arguments, and docstrings from the project.

## __init__.py

### Functions

- **setup_logging**()
  - Docstring: Set up logging configuration.
- **load_environment_variables**()
  - Docstring: No docstring available
- **initialize**()
  - Docstring: No docstring available

## app.py

### Functions

- **load_image_generator**(model_name)
  - Docstring: Function to load the ImageGenerator object.
- **save_image_helper**(image_data, identifier_helper)
  - Docstring: No docstring available
- **main**()
  - Docstring: Main function to run the Streamlit app to display generated images in a grid.

## text2img.py

### Functions

- **save_image**(self, path)
  - Docstring: Save the image to the specified path.
- **__init__**(self, model_name, cpu_offload, precision)
  - Docstring: Initializes the image generation pipeline with a specified model and precision.

Args:
    model_name (str): Name of the pretrained model to load.
    cpu_offload (bool): Flag to enable CPU offloading for the model.
    precision (torch.dtype): Precision for the model, defaults to torch.float16.
- **generate_image**(self, theme_prompt, subfolder, guidance_scale, height, width, num_inference_steps, max_sequence_length)
  - Docstring: Generates and saves an image based on the given prompt and settings.

Args:
    theme_prompt (str): Text prompt to guide image generation.
    subfolder (str): Subfolder to save the generated image.
    guidance_scale (float): Guidance scale to adjust adherence to the prompt.
    height (int): Height of the generated image in pixels.
    width (int): Width of the generated image in pixels.
    num_inference_steps (int): Number of steps for inference.
    max_sequence_length (int): Maximum sequence length for the prompt.

Returns:
    PictureData: Object containing the generated image metadata.
- **_prepare_image_metadata**(self, theme_prompt, subfolder)
  - Docstring: Function to prepare the image metadata based on the theme prompt.

### Class: ImageData

- **save_image**(self, path)
  - Docstring: Save the image to the specified path.

### Class: ImageGenerator

- **__init__**(self, model_name, cpu_offload, precision)
  - Docstring: Initializes the image generation pipeline with a specified model and precision.

Args:
    model_name (str): Name of the pretrained model to load.
    cpu_offload (bool): Flag to enable CPU offloading for the model.
    precision (torch.dtype): Precision for the model, defaults to torch.float16.
- **generate_image**(self, theme_prompt, subfolder, guidance_scale, height, width, num_inference_steps, max_sequence_length)
  - Docstring: Generates and saves an image based on the given prompt and settings.

Args:
    theme_prompt (str): Text prompt to guide image generation.
    subfolder (str): Subfolder to save the generated image.
    guidance_scale (float): Guidance scale to adjust adherence to the prompt.
    height (int): Height of the generated image in pixels.
    width (int): Width of the generated image in pixels.
    num_inference_steps (int): Number of steps for inference.
    max_sequence_length (int): Maximum sequence length for the prompt.

Returns:
    PictureData: Object containing the generated image metadata.
- **_prepare_image_metadata**(self, theme_prompt, subfolder)
  - Docstring: Function to prepare the image metadata based on the theme prompt.

## stock_categorizer.py

### Functions

- **get_category**(theme_prompt, client)
  - Docstring: Function which takes in a theme prompt and returns prepared picture prompt and additional metadata.

### Class: TaggedCategory


## prompt_generation.py

### Functions

- **get_picture_prompt**(theme_prompt, client)
  - Docstring: Function which takes in a theme prompt and returns prepared picture prompt and additional metadata.
- **get_categories**(self, llm_client)
  - Docstring: Extract the categories from the image prompt.

### Class: ImagePrompt

- **get_categories**(self, llm_client)
  - Docstring: Extract the categories from the image prompt.

## upscaler.py

### Functions

- **get_upscaler**(env)
  - Docstring: No docstring available
- **__init__**(self)
  - Docstring: Initialize the ImageUpscaler.
- **upscale_image**(self, input_path, save_path, prompt)
  - Docstring: Upscale a low-resolution image.

Args:
    input_path (str | Path): The path to the low-resolution input image.
    save_path (str | Path): The path to save the upscaled image.
    prompt (str): The textual description to guide the upscaling.
        Defaults to an empty string.

Returns:
    bool: True if the image was successfully upscaled, False otherwise.
- **upscale_and_save**(self, low_res_image, save_path, prompt)
  - Docstring: Upscale a low-resolution image and save it to the specified path.

Args:
    low_res_image (Image.Image | str | Path): The low-resolution
    input image or its filename.
    save_path (str): The path to save the upscaled image.
    prompt (str): The textual description to guide the upscaling.
    Defaults to an empty string.
- **upscale_folder**(self, folder_path, use_prompt, overwrite, file_format)
  - Docstring: Upscale all images in a folder and save them in the same folder.

use_prompt (bool): Whether to use the image filename as the
prompt for upscaling.
file_format (str | None): The format to save the upscaled images.
If None, the original format is used.

Returns:
    None
- **__init__**(self)
  - Docstring: Initializes the Upscaler class.

Currently, this constructor does not perform any operations.
- **upscale_image**(self, input_path, save_path, prompt)
  - Docstring: Upscale a low-resolution image using Real-ESRGAN.

Args:
    input_path (str | Path): The path to the low-res input image.
    save_path (str | Path): The path to save the upscaled image.
    prompt (str): The textual description to guide the upscaling.
        Defaults to an empty string.

Returns:
    bool: True if the image was successfully upscaled, False otherwise.
- **__init__**(self, model_id, device, dtype)
  - Docstring: Initialize the image upscaler pipeline.

Args:
    model_id (str): The model identifier from the Hugging Face hub.
    Defaults to UPSCALE_MODEL if not provided.
    device (str): Device to load the model
    onto ('cuda', 'cpu', or 'mps').
    dtype (torch.dtype): Data type for model weights.
    file_format (str): The format to save the upscaled images.
    Defaults to None.
    file_format (str): The format to save the upscaled images.
    Defaults to None.
- **upscale_image**(self, input_path, save_path, prompt)
  - Docstring: Upscale a low-resolution image using the pipeline.

input_path (str | Path): The path to the low-resolution input image.
save_path (str | Path): The path where the upscaled image will be
saved.
prompt (str, optional): The textual description to guide the
upscaling. Defaults to an empty string.

bool: True if the image was successfully upscaled and saved,
False otherwise.

### Class: ImageUpscaler

- **__init__**(self)
  - Docstring: Initialize the ImageUpscaler.
- **upscale_image**(self, input_path, save_path, prompt)
  - Docstring: Upscale a low-resolution image.

Args:
    input_path (str | Path): The path to the low-resolution input image.
    save_path (str | Path): The path to save the upscaled image.
    prompt (str): The textual description to guide the upscaling.
        Defaults to an empty string.

Returns:
    bool: True if the image was successfully upscaled, False otherwise.
- **upscale_and_save**(self, low_res_image, save_path, prompt)
  - Docstring: Upscale a low-resolution image and save it to the specified path.

Args:
    low_res_image (Image.Image | str | Path): The low-resolution
    input image or its filename.
    save_path (str): The path to save the upscaled image.
    prompt (str): The textual description to guide the upscaling.
    Defaults to an empty string.
- **upscale_folder**(self, folder_path, use_prompt, overwrite, file_format)
  - Docstring: Upscale all images in a folder and save them in the same folder.

use_prompt (bool): Whether to use the image filename as the
prompt for upscaling.
file_format (str | None): The format to save the upscaled images.
If None, the original format is used.

Returns:
    None

### Class: RealesrganUpscaler

- **__init__**(self)
  - Docstring: Initializes the Upscaler class.

Currently, this constructor does not perform any operations.
- **upscale_image**(self, input_path, save_path, prompt)
  - Docstring: Upscale a low-resolution image using Real-ESRGAN.

Args:
    input_path (str | Path): The path to the low-res input image.
    save_path (str | Path): The path to save the upscaled image.
    prompt (str): The textual description to guide the upscaling.
        Defaults to an empty string.

Returns:
    bool: True if the image was successfully upscaled, False otherwise.

### Class: DiffusionUpscaler

- **__init__**(self, model_id, device, dtype)
  - Docstring: Initialize the image upscaler pipeline.

Args:
    model_id (str): The model identifier from the Hugging Face hub.
    Defaults to UPSCALE_MODEL if not provided.
    device (str): Device to load the model
    onto ('cuda', 'cpu', or 'mps').
    dtype (torch.dtype): Data type for model weights.
    file_format (str): The format to save the upscaled images.
    Defaults to None.
    file_format (str): The format to save the upscaled images.
    Defaults to None.
- **upscale_image**(self, input_path, save_path, prompt)
  - Docstring: Upscale a low-resolution image using the pipeline.

input_path (str | Path): The path to the low-resolution input image.
save_path (str | Path): The path where the upscaled image will be
saved.
prompt (str, optional): The textual description to guide the
upscaling. Defaults to an empty string.

bool: True if the image was successfully upscaled and saved,
False otherwise.

## csv.py

### Functions

- **__init__**(self, image_dir, output_csv, category)
  - Docstring: Initialize the CSVGenerator.

Args:
    image_dir (str): Directory containing images.
    output_csv (str): Path to the output CSV file.
    category (int, optional): Default category for images.

Returns:
    None
- **get_category**(self, json_file)
  - Docstring: Get the category from the JSON file or use the default category.
- **create_csv**(self)
  - Docstring: Create a CSV file from images and their metadata.

### Class: CSVGenerator

- **__init__**(self, image_dir, output_csv, category)
  - Docstring: Initialize the CSVGenerator.

Args:
    image_dir (str): Directory containing images.
    output_csv (str): Path to the output CSV file.
    category (int, optional): Default category for images.

Returns:
    None
- **get_category**(self, json_file)
  - Docstring: Get the category from the JSON file or use the default category.
- **create_csv**(self)
  - Docstring: Create a CSV file from images and their metadata.

