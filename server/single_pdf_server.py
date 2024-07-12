from core import PdfReader
from config import Default
from core import OutputGenerator

if __name__ == "__main__":
    output_path_for_text = '/Users/apple/PycharmProjects/EPDLibrary/data/output/text'
    default = Default()
    outputGenerator = OutputGenerator()

    pdfReader = PdfReader(default.single_epd_path)
    pdfReader.read_pdf_text()
    text = pdfReader.get_text()

    outputGenerator.text_file_generator(text, output_path_for_text)

