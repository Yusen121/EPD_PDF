import os
from log.log import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TxtOperator:
    @staticmethod
    def split_text_file(input_path, output_path, chunk_size=1000, chunk_overlap=0):
        # Step 1: Read the text file
        with open(input_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Step 2: Create an instance of RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["#"]
        )

        # Step 3: Split the text
        chunks = splitter.split_text(text)

        # Step 4: Create the output folder if it doesn't exist
        output_folder_path = os.path.join(output_path, 'txt')
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        # Step 5: Write each chunk to a new text file in the output folder
        for i, chunk in enumerate(chunks):
            chunk_filename = os.path.join(output_folder_path, f"chunk_{i + 1}.txt")
            with open(chunk_filename, 'w', encoding='utf-8') as chunk_file:
                chunk_file.write(chunk)

        logger.info(f"Text has been split into {len(chunks)} files and saved to '{output_folder_path}'.")


if __name__ == "__main__":
    input_path = "/Users/apple/PycharmProjects/pdf_server_2.1/core/server/inference_results/www.environdec.com:library:epd872/www.environdec.com:library:epd872.txt"
    output_folder = "/Users/apple/PycharmProjects/pdf_server_2.1/core/server/inference_results/www.environdec.com:library:epd872"
    TxtOperator.split_text_file(input_path, output_folder)
