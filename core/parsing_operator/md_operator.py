from pathlib import Path
from log.log import logger


class MdOperator:

    # EFFECTS: Transforms the contents of a Markdown (.md) file into a plain text (.txt) file.
    # The output path can be specified; if not, the .txt file will be saved in the same directory as the .md file.
    @staticmethod
    def md_to_txt(input_path, output_path=None):
        input_path = Path(input_path)

        # Check if the input file is a Markdown file
        if not input_path.is_file() or input_path.suffix != '.md':
            logger.error("The provided path is not a valid Markdown file.")
            return

        # Determine the output path
        if output_path:
            output_path = Path(output_path)
            if output_path.is_dir():
                # If output_path is a directory, save the file with the same name but .txt extension
                output_path = output_path / (input_path.stem + '.txt')
        else:
            # Default: save the .txt file in the same directory as the .md file
            output_path = input_path.with_suffix('.txt')

        try:
            # Read the content of the .md file
            with input_path.open('r', encoding='utf-8') as md_file:
                content = md_file.read()

            # Write the content to a .txt file
            with output_path.open('w', encoding='utf-8') as txt_file:
                txt_file.write(content)

            logger.info(f"Markdown file has been successfully transformed into a text file: {output_path}")

        except Exception as e:
            logger.error(f"An error occurred while transforming the Markdown file: {e}, the md file path is {input_path}")



# Example usage
if __name__ == "__main__":
    path = '/Users/apple/PycharmProjects/pdf_server_2.1/result/magic-pdf/www.environdec.com:library:epd1347/auto/www.environdec.com:library:epd1347.md'
    output_path = '/Users/apple/PycharmProjects/pdf_server_2.1/test/txt'
    MdOperator.md_to_txt(path, output_path)
