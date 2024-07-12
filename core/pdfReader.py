from config import Default
import fitz


class PdfReader:
    # EFFECTS: get the information of the exist pdf file by the pdf path
    def __init__(self, pdf_path):
        self.path = pdf_path
        self.doc = None
        self.text = ""

    # MODIFIES: self
    def read_pdf_text(self):
        self.__open_pdf()
        self.__load_text()

    # MODIFIES: self
    def __open_pdf(self):
        self.doc = fitz.open(self.path)

    # MODIFIES: self
    def __load_text(self):
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            text = page.get_text()
            self.text += text + '\n'

    # EFFECTS: return the text
    def get_text(self):
        return self.text

    # EFFECTS: return the doc
    def get_doc(self):
        return self.doc


if __name__ == '__main__':
    default = Default()
    pdfReader = PdfReader(default.single_epd_path)
    pdfReader.read_pdf_text()
    pdfReader.get_text()
