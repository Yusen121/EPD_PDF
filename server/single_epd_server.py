from core import Processor

if __name__ == "__main__":
    path = '/Users/apple/PycharmProjects/EPDLibrary/data/input/try_1/Data (1).pdf'
    output_path = '/Users/apple/PycharmProjects/EPDLibrary/server/output'
    processor = Processor()
    processor.single_pdf_processor_miner_u(path, output_path)