import glob
import os
import traceback

import pandas as pd
import uuid
import time
from tqdm import tqdm
from log.log import logger
from pathlib import Path
from config import Default
from config.default import Default
from core.extractor.pdf_extractor import PdfExtractor
from core.extractor.text_extractor import TextExtractor
from core.extractor.table_extractor import TableExtractor
from core.parsing_operator import PDFOperator, ImageOperate, MdOperator, TxtOperator
from core.standardize.csv_reformat import CsvReformat
from core.generator.csv_generator import CsvGenerator
from core.tools import Finder


class Processor:
    uuid = uuid

    def __init__(self):
        self.default = Default()

    @staticmethod
    def single_txt_processor(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except Exception as e:
            # Handle exception if needed
            raise e
        return content

    @staticmethod
    def multiple_txt_processor(folder_path):
        txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
        contents = []
        for txt_file in txt_files:
            try:
                content = Processor.single_txt_processor(txt_file)
                contents.append(content)
            except Exception as e:
                logger.error(f'There is an error in this txt file: {txt_file}, in this folder: {folder_path}')
        return contents

    @staticmethod
    def multiple_csv_processor(folder_path):
        csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
        contents = []
        for csv_file in csv_files:
            content = pd.read_csv(csv_file)
            contents.append(content)
        return contents

    # url 查重
    def single_pdf_processor(self, single_pdf_path, output_path, method='split_method'):
        generate_uuid = str(uuid.uuid4())

        # Optimize: source_url
        source_url = os.path.basename(single_pdf_path)

        pdfs_output_path = os.path.join(output_path, 'pdf')

        pdf_output_folder_path = os.path.join(pdfs_output_path, source_url)
        if not os.path.exists(pdf_output_folder_path):
            os.makedirs(pdf_output_folder_path)

        pdf_extractor = PdfExtractor(single_pdf_path)
        text_extractor = TextExtractor()
        table_extractor = TableExtractor()
        csv_reformat = CsvReformat()

        pdf_extractor.tables_extract(pdf_output_folder_path, method)

        # Reformat
        split_folder_path = os.path.join(pdf_output_folder_path, 'split_method')
        csv_reformat.reformat_all_csvs_in_folder(split_folder_path, pdf_output_folder_path)

        # Texts extract
        texts = self.multiple_txt_processor(split_folder_path)
        text_extractor.multiple_text_extract(texts)
        text_extractor.show_extract_content()

        # Table extract
        standardize_folder_path = os.path.join(pdf_output_folder_path, 'standardize')
        dfs = self.multiple_csv_processor(standardize_folder_path)
        table_extractor.multiple_dfs_extracts(dfs)
        table_extractor.show_value()

        # csv generate
        csv_generator = CsvGenerator(generate_uuid, table_extractor, text_extractor, output_path, source_url)
        csv_generator.generate_csv()

    def single_pdf_processor_miner_u(self, single_pdf_folder_path, output_path):
        generate_uuid = str(uuid.uuid4())

        source_url = os.path.basename(single_pdf_folder_path)

        csv_output_folder_path = os.path.join(single_pdf_folder_path, 'csv')

        csv_standardize_folder_path = os.path.join(single_pdf_folder_path, 'csv_standardize')
        if not os.path.exists(csv_standardize_folder_path):
            os.makedirs(csv_standardize_folder_path)

        text_extractor = TextExtractor()
        table_extractor = TableExtractor()
        csv_reformat = CsvReformat()

        csv_reformat.reformat_all_csvs_in_folder_2(csv_output_folder_path, csv_standardize_folder_path)

        # Texts extract
        text_folder_path = os.path.join(single_pdf_folder_path, 'txt')
        texts = self.multiple_txt_processor(text_folder_path)
        try:
            text_extractor.multiple_text_extract(texts)
        except Exception as e:
            logger.error(f'There is an error here {e}, need to check the txt folder {text_folder_path}')

        # text_extractor.show_extract_content()

        # Table extract
        table_extractor.multiple_csvs_extracts(csv_standardize_folder_path)
        # table_extractor.show_value()

        # csv generate
        csv_generator = CsvGenerator(generate_uuid, table_extractor, text_extractor, output_path, source_url)
        csv_generator.generate_csv()

    def process_pdfs_in_folder(self, input_folder, output_folder):
        # Get a list of all PDF files in the input folder
        pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

        # Process each PDF file with a progress bar
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
            single_epd_path_using = os.path.join(input_folder, pdf_file)
            self.single_pdf_processor(single_epd_path_using, output_folder)
            print(f"Processed {pdf_file}")

    def process_pdf_folders_miner_u(self, input_folder, output_folder):
        # Get a list of all folders inside the input_folder
        start_time = time.time()
        logger.info(f"Process started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

        pdf_folders = [f for f in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, f))]

        # Adding a progress bar for folder processing
        for folder in tqdm(pdf_folders, desc="Processing folders", unit="folder"):
            folder_start_time = time.time()
            logger.info(
                f"Processing folder '{folder}' started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(folder_start_time))}")

            folder_path = os.path.join(input_folder, folder)
            try:
                self.single_pdf_processor_miner_u(folder_path, output_folder)
            except Exception as e:
                logger.error(f"Error processing folder '{folder}': {str(e)}")
                logger.error(traceback.format_exc())
            folder_end_time = time.time()
            elapsed_time = folder_end_time - folder_start_time
            logger.info(
                f"Processing folder '{folder}' finished at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(folder_end_time))}. Time taken: {elapsed_time:.2f} seconds")

        end_time = time.time()
        total_elapsed_time = end_time - start_time
        logger.info(
            f"Process finished at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}. Total time taken: {total_elapsed_time:.2f} seconds")

    # def process_pdf_folders_miner_u(self, input_folder, output_folder):
    #     # Get a list of all folders inside the input_folder
    #     start_time = time.time()
    #     print(f"Process started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    #
    #     pdf_folders = [f for f in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, f))]
    #
    #     for folder in pdf_folders:
    #         folder_start_time = time.time()
    #         print(
    #             f"Processing folder '{folder}' started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(folder_start_time))}")
    #
    #         folder_path = os.path.join(input_folder, folder)
    #         self.single_pdf_processor_miner_u(folder_path, output_folder)
    #         folder_end_time = time.time()
    #         elapsed_time = folder_end_time - folder_start_time
    #         print(
    #             f"Processing folder '{folder}' finished at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(folder_end_time))}. Time taken: {elapsed_time:.2f} seconds")
    #
    #     end_time = time.time()
    #     total_elapsed_time = end_time - start_time
    #     print(
    #         f"Process finished at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}. Total time taken: {total_elapsed_time:.2f} seconds")

    def miner_u_total(self, pdf_folder_path, output_path):
        magic_pdf_path = self.default.magic_pdf_path
        inference_path = os.path.join(output_path, 'inference_path')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # Object
        pdf_operator = PDFOperator()
        image_operator = ImageOperate(inference_path)
        # Step 1, process the pdf_file
        pdf_operator.process_folder(pdf_folder_path, magic_pdf_path)
        # Step 2

        # Adding a progress bar for folder processing
        folders = [folder for folder in magic_pdf_path.iterdir() if folder.is_dir() and folder.name != ".DS_Store"]

        for folder in tqdm(folders, desc="Processing folders", unit="folder"):
            name_recorded = folder.name
            try:
                image_folder_path = Finder.find_folder('images', folder)
                md_path = Finder.find_md_folder(name_recorded, folder)

                image_operator.process_folder(image_folder_path, name_recorded, True)
                single_pdf_output_path = image_operator.get_result_folder_path()

                MdOperator.md_to_txt(md_path, single_pdf_output_path)
                txt_path = os.path.join(single_pdf_output_path, f'{name_recorded}.txt')
                TxtOperator.split_text_file(txt_path, single_pdf_output_path)
            except Exception as e:
                logger.error(f"There is an error when processing {folder} in magic pdf")

        processor = Processor()
        processor.process_pdf_folders_miner_u(inference_path, output_path)

    # def miner_u_total(self, pdf_folder_path, output_path):
    #     magic_pdf_path = self.default.magic_pdf_path
    #     inference_path = os.path.join(output_path, 'inference_path')
    #     if not os.path.exists(output_path):
    #         os.makedirs(output_path)
    #     # Object
    #     pdf_operator = PDFOperator()
    #     image_operator = ImageOperate(inference_path)
    #     # Step 1, process the pdf_file
    #     pdf_operator.process_folder(pdf_folder_path, magic_pdf_path)
    #     # Step 2
    #
    #     for folder in magic_pdf_path.iterdir():
    #         if folder.is_dir() and folder.name != ".DS_Store":
    #             name_recorded = folder.name
    #             try:
    #                 image_folder_path = Finder.find_folder('images', folder)
    #                 md_path = Finder.find_md_folder(name_recorded, folder)
    #
    #                 image_operator.process_folder(image_folder_path, name_recorded, True)
    #                 single_pdf_output_path = image_operator.get_result_folder_path()
    #
    #                 MdOperator.md_to_txt(md_path, single_pdf_output_path)
    #                 txt_path = os.path.join(single_pdf_output_path, f'{name_recorded}.txt')
    #                 TxtOperator.split_text_file(txt_path, single_pdf_output_path)
    #             except Exception as e:
    #                 logger.error(f"There is an error when processing {folder} in magic pdf")
    #
    #     processor = Processor()
    #     processor.process_pdf_folders_miner_u(inference_path, output_path)


if __name__ == "__main__":
    processor = Processor()
    folder_path = '/Users/apple/PycharmProjects/pdf_server_2.1/core/server/inference_results'
    output_path = '/Users/apple/PycharmProjects/pdf_server_2.1/core/server/result_3'
    processor.process_pdf_folders_miner_u(folder_path, output_path)

    file_path = '/Users/apple/PycharmProjects/pdf_server_2.1/core/server/inference_results/www.environdec.com:library:epd1128'
    # processor.single_pdf_processor_miner_u(file_path, output_path)
