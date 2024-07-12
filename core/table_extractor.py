import csv
import os.path
import pdfplumber
import pandas as pd
from config import Default
from pdf2image import convert_from_path
from PIL import Image
from tools import TableCleaning
import pytesseract
from openpyxl import Workbook

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Adjust based on `which tesseract` output


class TableExtractor:

    def __init__(self, pdf_path):
        self.path = pdf_path

    @staticmethod
    # EFFECTS: return whether table is completely empty
    def __is_empty_table(table):
        table_cleaning = TableCleaning(table)
        return table_cleaning.is_all_null()

    @staticmethod
    def __convert_to_grayscale(image):
        return image.convert("L")

    @staticmethod
    def __extract_text(image):
        return pytesseract.image_to_string(image)

    @staticmethod
    def __extract_table_data(text):
        rows = text.strip().split("\n")
        table_data = [row.split("\t") for row in rows]
        return table_data

    @staticmethod
    def __save_as_excel(table_data, output_path):
        workbook = Workbook()
        sheet = workbook.active
        for row_index, row_data in enumerate(table_data, start=1):
            for column_index, cell_data in enumerate(row_data, start=1):
                sheet.cell(row=row_index, column=column_index, value=cell_data)
        workbook.save(output_path)

    @staticmethod
    def __save_as_csv(table_data, output_path):
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in table_data:
                writer.writerow(row)

    # Using pdfplumber:
    # EFFECTS: return the tables in pdf
    def __simple_method(self):
        with pdfplumber.open(self.path) as pdf:
            all_table = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    all_table.append(table)
        return all_table

    # MODIFIES: this
    def __images_method(self, output_folder, dpi=300):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Convert PDF to a list of images
        images = convert_from_path(self.path, dpi=dpi)
        i = 0

        # Save images to the specified output folder
        for _, image in enumerate(images):
            i += 1
            # excel generate
            using_image = self.__convert_to_grayscale(image)
            using_text = self.__extract_text(using_image)
            using_table = self.__extract_table_data(using_text)
            excel_path = f"{output_folder}/table_{i}.xlsx"
            csv_path = f"{output_folder}/table_{i}.csv"
            self.__save_as_excel(using_table, excel_path)
            self.__save_as_csv(using_table, csv_path)
            # image_method saving
            image_path = f"{output_folder}/page_{i}.png"
            image.save(image_path, 'PNG')
            print(f"Saved: {image_path}")

    def __split_method(self, pdf_path, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract tables
                tables = page.extract_tables()
                print(tables)
                table_bboxes = []
                if tables:
                    table_counter = 0
                    for i, table in enumerate(tables):
                        if table:
                            if not self.__is_empty_table(table):
                                table_clean = TableCleaning(table)
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df = table_clean.remove_null_rows_and_columns(df)
                                if (not table_clean.is_dataframe_all_null(df)
                                        and not table_clean.is_small_amount_cells(df)):

                                    # Optimize: seems problem happened in tables
                                    # df = table_clean.rotate_vertical_text(df)

                                    table_counter += 1
                                    csv_path = os.path.join(output_folder,
                                                            f"table_page_{page_num + 1}_table_{table_counter}.csv")
                                    df.to_csv(csv_path, index=False)
                                    print(f"Extracted table to {csv_path}")

                            # Get the bounding box of the table
                            table_bbox = page.find_tables()[i].bbox
                            table_bboxes.append(table_bbox)

                # Extract text excluding the table regions
                text = ''
                if table_bboxes:
                    for char in page.chars:
                        in_table = False
                        for bbox in table_bboxes:
                            if bbox[0] <= char['x0'] <= bbox[2] and bbox[1] <= char['top'] <= bbox[3]:
                                in_table = True
                                break
                        if not in_table:
                            text += char['text']
                else:
                    text = page.extract_text()

                if text:
                    text_path = os.path.join(output_folder, f"text_page_{page_num + 1}.txt")
                    with open(text_path, 'w', encoding='utf-8') as text_file:
                        text_file.write(text)
                    print(f"Extracted text to {text_path}")

    def tables_extract(self, output_folder_path, model='split_method'):
        if model == 'simple':
            tables = self.__simple_method()
            i = 0
            for _, table in enumerate(tables):
                if not self.__is_empty_table(table):
                    df = pd.DataFrame(table)
                    i += 1
                    csv_path = os.path.join(output_folder_path, f'table_{i}.csv')
                    df.to_csv(csv_path, index=False)
        if model == 'image_method':
            self.__images_method(output_folder_path)

        if model == 'split_method':
            self.__split_method(self.path, output_folder_path)


if __name__ == "__main__":
    default = Default()
    table_extractor = TableExtractor(default.single_epd_path)
    # # Test simple_method
    # output_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/csv'
    # table_extractor.tables_extract(output_path, 'simple')
    # # Test image_method:
    # image_folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/image'
    # table_extractor.tables_extract(image_folder_path, "image_method")
    # Test split_method
    split_folder = '/Users/apple/PycharmProjects/EPDLibrary/data/output/split_method'
    table_extractor.tables_extract(split_folder, "split_method")
