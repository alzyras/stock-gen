import os
import subprocess
import shutil
import time

def upscale_images(input_dir, output_dir, used_dir, upscale_factor=4):
    model = 'realesrgan-x4plus'

    # Ensure necessary directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(used_dir, exist_ok=True)

    # Iterate over all PNG images in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.png'):
            input_image_path = os.path.join(input_dir, filename)
            output_image_path = os.path.join(output_dir, filename.replace('.png', '.jpg'))
            json_filename = filename.replace('.png', '.json')
            input_json_path = os.path.join(input_dir, json_filename)
            output_json_path = os.path.join(output_dir, json_filename)

            # Enhance image using Real-ESRGAN
            enhance_command = [
                './realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan', '-i', input_image_path, '-o', output_image_path,
                '-n', model, '-s', str(upscale_factor), '-f', 'jpg'
            ]

            try:
                result = subprocess.run(enhance_command, check=True, capture_output=True, text=True)
                print(f"Enhancing {input_image_path} to {output_image_path}")
                print(result.stdout)
                print(result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Error during image enhancement for {input_image_path}: {e}")
                print(e.stdout)
                print(e.stderr)
                continue

            # Move original image and JSON to used folder
            try:
                shutil.move(input_image_path, os.path.join(used_dir, filename))
                print(f"Moved {input_image_path} to {os.path.join(used_dir, filename)}")
                if os.path.exists(input_json_path):
                    shutil.move(input_json_path, os.path.join(used_dir, json_filename))
                    print(f"Moved {input_json_path} to {os.path.join(used_dir, json_filename)}")
            except Exception as e:
                print(f"Error moving file {input_image_path} or {input_json_path} to {used_dir}: {e}")
                continue

            # Copy JSON to output folder
            try:
                if os.path.exists(os.path.join(used_dir, json_filename)):
                    shutil.copy(os.path.join(used_dir, json_filename), output_json_path)
                    print(f"Copied {os.path.join(used_dir, json_filename)} to {output_json_path}")
            except Exception as e:
                print(f"Error copying file {os.path.join(used_dir, json_filename)} to {output_json_path}: {e}")
                continue

            print(f"Upscaled {filename} and saved to {output_image_path}")

if __name__ == '__main__':
    input_dir = 'store/generated_images/adobe_stock'
    output_dir = 'store/generated_images/adobe_stock_upscaled'
    used_dir = 'store/generated_images/adobe_stock/used'

    # Start timing
    start_time = time.time()

    # Upscale images
    upscale_images(input_dir, output_dir, used_dir)

    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    elapsed_hours = elapsed_minutes / 60

    print(f"Upscaling images took {elapsed_minutes:.2f} minutes, aka ({elapsed_hours:.2f} hours).")
