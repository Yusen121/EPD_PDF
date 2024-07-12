import os


class OutputGenerator:
    def __init__(self):
        pass

    @staticmethod
    def text_file_generator(pdf_text, output_path):
        with open(os.path.join(output_path, 'extracted_text.txt'), "w", encoding="utf-8") as text_file:
            text_file.write(pdf_text)

    # @staticmethod
    # def json_file_generator(pdf_text, output_path):
    #     with open(os.path.join(output_path, 'extracted_text.json'), "w", encoding="utf-8") as json_file:
    #         json.dump({"text": pdf_text}, json_file, ensure_ascii=False, indent=4)
    #
    # @staticmethod
    # def csv_file_generator(pdf_text, output_path):
    #     with open(os.path.join(output_path, 'extracted_text.table_method'), "w", encoding="utf-8", newline='') as csv_file:
    #         writer = table_method.writer(csv_file)
    #         writer.writerow(["Page", "Text"])
    #         for page_num, page_text in enumerate(pdf_text.split('\n\n'), 1):
    #             writer.writerow([page_num, page_text])
