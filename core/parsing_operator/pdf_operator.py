import subprocess
from log.log import logger
from pathlib import Path


class PDFOperator:
    def __init__(self):
        pass

    def run_magic_pdf(self, pdf_path):
        # Define the command to run
        command = [
            "magic-pdf",
            "pdf-command",
            "--pdf", pdf_path
        ]

        try:
            # Execute the command
            subprocess.run(command, check=True)
            # print(f"Command executed successfully for {pdf_path}.")
            logger.info(f"Command executed successfully for {pdf_path}.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed for {pdf_path} with error: {e}")

    def process_folder(self, folder_path, output_path):
        folder_path = Path(folder_path)

        # Iterate through all PDFs in the folder
        for pdf_file in folder_path.glob('*.pdf'):
            folder_name = pdf_file.stem
            folder_to_check = output_path / folder_name

            if folder_to_check.exists() and folder_to_check.is_dir():
                logger.info(f"Folder '{folder_name}' already exists. Skipping {pdf_file.name}.")
                continue
            logger.info(f"Processing PDF: {pdf_file.name}")
            self.run_magic_pdf(str(pdf_file))



if __name__ == "__main__":
    pdf_operator = PDFOperator()
    pdf_operator.process_folder('/Users/apple/PycharmProjects/pdf_server_2.1/pdf')
