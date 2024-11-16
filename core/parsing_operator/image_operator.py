from pathlib import Path
from rapid_table import RapidTable, VisTable
from rapidocr_onnxruntime import RapidOCR
from bs4 import BeautifulSoup
from log.log import logger
import csv
import uuid
import os


class ImageOperate:
    def __init__(self, output_dir="./inference_results/"):
        self.result_folder = None
        self.ocr_engine = RapidOCR()
        self.table_engine = RapidTable()
        self.viser = VisTable()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.table_html_str = None
        self.table_cell_bboxes = None

    def process_image(self, img_path, save_dir, by_type=False):
        img_path = Path(img_path)

        # Perform OCR on the image
        ocr_result, _ = self.ocr_engine(img_path)

        # Generate HTML table from OCR results
        self.table_html_str, self.table_cell_bboxes, _ = self.table_engine(img_path, ocr_result)

        # Save the HTML, CSV, and visualization in the appropriate folder
        if by_type:
            self.save_results_by_type(img_path, save_dir)
        else:
            self.save_results(img_path, save_dir)

        # Print the HTML string (for debugging or informational purposes)
        print(self.table_html_str)

        return self.table_html_str

    def save_results(self, img_path, save_dir):
        # Create a folder for the image using the image's name (without extension)
        img_folder = save_dir / img_path.stem
        img_folder.mkdir(parents=True, exist_ok=True)

        # Save the HTML representation of the table
        save_html_path = img_folder / f"{img_path.stem}.html"
        with open(save_html_path, 'w') as file:
            file.write(self.table_html_str)

        # Save the visualization image
        save_drawed_path = img_folder / f"vis_{img_path.name}"
        self.viser(img_path, self.table_html_str, save_html_path, self.table_cell_bboxes, save_drawed_path)

        # Convert HTML to CSV
        self.convert_html_to_csv(save_html_path, img_folder)

    def save_results_by_type(self, img_path, save_dir):
        # Create folders for each type: jpg, csv, and html
        jpg_folder = save_dir / "jpg"
        html_folder = save_dir / "html"
        csv_folder = save_dir / "csv"

        jpg_folder.mkdir(parents=True, exist_ok=True)
        html_folder.mkdir(parents=True, exist_ok=True)
        csv_folder.mkdir(parents=True, exist_ok=True)

        # Save the HTML representation of the table
        save_html_path = html_folder / f"{img_path.stem}.html"
        with open(save_html_path, 'w') as file:
            file.write(self.table_html_str)

        # Save the visualization image
        save_drawed_path = jpg_folder / f"vis_{img_path.name}"
        self.viser(img_path, self.table_html_str, save_html_path, self.table_cell_bboxes, save_drawed_path)

        # Convert HTML to CSV
        self.convert_html_to_csv(save_html_path, csv_folder)

    def convert_html_to_csv(self, html_file_path, save_dir):
        csv_file_path = save_dir / f"{html_file_path.stem}.csv"

        # Read the HTML content
        with open(html_file_path, 'r') as file:
            html_content = file.read()

        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the table in the HTML
        table = soup.find('table')

        # Open a CSV file for writing
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Iterate over each row in the table
            for row in table.find_all('tr'):
                # Extract the text from each cell in the row
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]

                # Write the row data to the CSV file
                writer.writerow(row_data)

        print(f"CSV file has been saved to: {csv_file_path}")
        return csv_file_path

    def process_folder(self, folder_path, result_folder_name=None, by_type=False):
        folder_path = Path(folder_path)

        # Create a new folder inside the output_dir
        if result_folder_name is None:
            result_folder_name = str(uuid.uuid4())
        result_folder = self.output_dir / result_folder_name
        result_folder.mkdir(parents=True, exist_ok=True)
        self.result_folder = result_folder

        # Iterate through all images in the folder
        for img_file in folder_path.glob('*.jpg'):
            try:
                logger.info(f"Processing image: {img_file.name}")
                self.process_image(img_file, result_folder, by_type)
            except Exception as e:
                logger.error(f'The error report is: {e}, the error img_file is {img_file}')

        logger.info(f"All images in {folder_path} have been processed and saved to {result_folder}.")

    def get_result_folder_path(self):
        return self.result_folder


if __name__ == "__main__":
    image_op = ImageOperate()
    path = '/Users/apple/PycharmProjects/pdf_server_2.1/images'
    image_op.process_folder(path, by_type=True)
