import traceback
from core import Processor
from log.log import logger

if __name__ == "__main__":
    # Path
    pdf_folder_path = '/Users/apple/PycharmProjects/pdf_server_2.1/pdf'
    output_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result_2'
    processor = Processor()
    try:
        processor.miner_u_total(pdf_folder_path, output_path)
    except Exception as e:
        logger.error(f'The error is: {e}')
        logger.error(traceback.format_exc())  # Logs the traceback
