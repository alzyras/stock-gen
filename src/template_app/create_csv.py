import os
import json
import csv

def create_csv_from_images_and_jsons(image_dir, output_csv):
    # Define the category
    category = 12

    # Prepare the CSV header
    header = ["Filename", "Title", "Keywords", "Category"]

    # Open the CSV file for writing
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

        # Iterate over all PNG files in the directory
        for filename in os.listdir(image_dir):
            if filename.endswith(".jpg"):
                # Construct the corresponding JSON filename
                json_filename = os.path.splitext(filename)[0] + ".json"
                json_path = os.path.join(image_dir, json_filename)

                # Read the JSON file
                if os.path.exists(json_path):
                    with open(json_path, 'r') as json_file:
                        data = json.load(json_file)
                        title = data.get("title", "")
                        tags = data.get("tags", [])
                        keywords = ",".join(tags)

                        # Write the row to the CSV file
                        writer.writerow([filename, title, keywords, category])

if __name__ == "__main__":
    image_directory = "/Users/tomastiminskas/swarmui/python-template/store/generated_images/adobe_stock_upscaled/"
    output_csv_path = "/Users/tomastiminskas/swarmui/python-template/src/template_app/generated_images.csv"
    create_csv_from_images_and_jsons(image_directory, output_csv_path)