import os

from core import Processor


# def process_pdfs_in_folder(input_folder, output_path):
#     processor_use = Processor()
#
#     # Get a list of all PDF files in the input folder
#     pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
#
#     # Process each PDF file
#     for pdf_file in pdf_files:
#         single_epd_path = os.path.join(input_folder, pdf_file)
#         processor_use.single_pdf_processor(single_epd_path, output_path)
#         print(f"Processed {pdf_file}")


if __name__ == "__main__":
    processor = Processor()
    epd_folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data/input/folder_22'
    output_folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output'
    processor.process_pdfs_in_folder(epd_folder_path, output_folder_path)

