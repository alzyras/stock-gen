import csv
import json
import os
from pathlib import Path


class CSVGenerator:
    """Generate CSV file for uploading to Adobe Stock.

    Initialize the CSVGenerator with the image directory,
    output CSV path, and category.
    """

    def __init__(
        self,
        image_dir: str,
        output_csv: str,
        category: int | None = None,
    ) -> None:
        """Initialize the CSVGenerator.

        Args:
            image_dir (str): Directory containing images.
            output_csv (str): Path to the output CSV file.
            category (int, optional): Default category for images.

        Returns:
            None
        """
        self.image_dir = image_dir
        self.output_csv = output_csv
        self.category = category
        self.category_dict = {
            "Animals": 1,
            "Buildings and Architecture": 2,
            "Business": 3,
            "Drinks": 4,
            "The Environment": 5,
            "States of Mind": 6,
            "Food": 7,
            "Graphic Resources": 8,
            "Hobbies and Leisure": 9,
            "Industry": 10,
            "Landscapes": 11,
            "Lifestyle": 12,
            "People": 13,
            "Plants and Flowers": 14,
            "Culture and Religion": 15,
            "Science": 16,
            "Social Issues": 17,
            "Sports": 18,
            "Technology": 19,
            "Transport": 20,
            "Travel": 21,
        }

    def get_category(self, json_file: dict) -> int:
        """Get the category from the JSON file or use the default category."""
        if self.category is not None:
            return self.category

        category = json_file["category"]
        if isinstance(category, int):
            self.category = category
            return category

        # Assuming self.category_dict is a dictionary that maps category names
        # to numbers
        self.category = self.category_dict.get(category, None)
        return self.category

    def create_csv(self) -> None:
        """Create a CSV file from images and their metadata."""
        # Prepare the CSV header
        header = ["Filename", "Title", "Keywords", "Category"]

        # Open the CSV file for writing
        with Path(self.output_csv).open(mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)

            # Iterate over all JPG files in the directory
            for filename in os.listdir(self.image_dir):
                if filename.endswith(".png"):
                    # Construct the corresponding JSON filename
                    json_filename = Path(filename).stem + ".json"
                    json_path = Path(self.image_dir) / json_filename

                    # Read the JSON file
                    if Path(json_path).exists():
                        with Path(json_path).open(
                            encoding="utf-8",
                        ) as json_file:
                            data = json.load(json_file)
                            title = data.get("title", "")
                            tags = data.get("tags", [])
                            keywords = ",".join(tags)

                            # Write the row to the CSV file
                            writer.writerow(
                                [
                                    filename,
                                    title,
                                    keywords,
                                    self.get_category(data),
                                ],
                            )


if __name__ == "__main__":
    IMAGE_DIRECTORY = "image_store"
    OUTPUT_CSV_PATH = "generated_images.csv"
    csv_generator = CSVGenerator(IMAGE_DIRECTORY, OUTPUT_CSV_PATH)
    csv_generator.create_csv()
