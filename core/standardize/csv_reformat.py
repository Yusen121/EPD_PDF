import os
import pandas as pd
import re
from core.storage.file_storage import FileStorage
from log.log import logger
from tools import TableCleaning


class CsvReformat:
    storage = FileStorage()

    def __init__(self, csv_path=None):
        self.csv_path = csv_path
        if csv_path:
            try:
                self.df = pd.read_csv(csv_path, on_bad_lines='skip')
                self.csv_name = os.path.basename(csv_path)
            except Exception as e:
                raise Exception(f"The error csv path is {csv_path}, the error info is {e}")

    @classmethod
    def reformat_all_csvs_in_folder(cls, folder_path, output_path):
        standardize_output_path = os.path.join(output_path, 'standardize')
        if not os.path.exists(standardize_output_path):
            os.makedirs(standardize_output_path)
        csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
        for csv_file in csv_files:
            try:
                file_path = os.path.join(folder_path, csv_file)
                reformat = cls(file_path)
                reformat.apply_csv_reformat(standardize_output_path)
            except Exception as e:
                print(f'The Error file is {e}, with the folder_path {folder_path}, and the name is: {csv_file}')

    @classmethod
    def reformat_all_csvs_in_folder_2(cls, folder_path, output_path):
        csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
        for csv_file in csv_files:
            try:
                file_path = os.path.join(folder_path, csv_file)
                reformat = cls(file_path)
                reformat.apply_csv_reformat(output_path)
            except Exception as e:
                logger.error(f'There is an error in the csv file {csv_file} in this folder {folder_path}')


    # def apply_csv_reformat(self, output_path):
    #     print("Initial DataFrame:")
    #     print(self.df)  # Show initial state
    #     df = self.df
    #
    #     self.df = self.df.applymap(self.__remove_line_break)
    #     print("After removing line breaks:")
    #     print(self.df)
    #     df = self.df
    #
    #     self.df = self.df.applymap(self.__replace_unnamed_cells)
    #     print("After replacing unnamed cells:")
    #     print(self.df)
    #     df = self.df
    #
    #     self.df = self.df.applymap(self.__replace_hyphen)
    #     print("After replacing hyphens:")
    #     print(self.df)
    #     df = self.df
    #
    #     self.__replace_unnamed_columns()
    #     print("After replacing unnamed columns:")
    #     print(self.df)
    #     df = self.df
    #
    #     self.__set_new_header()
    #     print("After setting a new header:")
    #     print(self.df)
    #     df = self.df
    #
    #     self.__csv_storage(output_path)
    #     print(f"Final DataFrame saved to {output_path}")

    def apply_csv_reformat(self, output_path):
        self.df = self.df.applymap(self.__remove_line_break)
        self.df = self.df.applymap(self.__replace_unnamed_cells)
        self.df = self.df.applymap(self.__replace_hyphen)
        self.__replace_unnamed_columns()
        self.__set_new_header()
        self.__csv_storage(output_path)

    def __csv_storage(self, output_path):
        self.storage.standardize_storage(self.df, self.csv_name, output_path)

    @staticmethod
    def __remove_line_break(text):
        if isinstance(text, str) and '\n' in text:
            return text.replace('\n', '')
        return text

    def __replace_unnamed_columns(self):
        self.df.columns = [re.sub(r'Unnamed: \d+', '', col) for col in self.df.columns]
        self.df.columns = [col.replace('Results per 1 m3 of concrete', '').strip()
                           for col in self.df.columns]

    def __set_new_header(self):
        if all(col == '' for col in self.df.columns):
            new_header = self.df.iloc[0]
            self.df = self.df.iloc[1:]
            self.df.columns = new_header

    @staticmethod
    def __replace_unnamed_cells(cell):
        if isinstance(cell, str) and re.match(r'Unnamed: \d+', cell):
            return ''
        return cell

    @staticmethod
    def __replace_hyphen(cell):
        if isinstance(cell, str) and cell.strip() == '-':
            return cell.replace('-', '')
        return cell

    @staticmethod
    def clean_csv_data(input_file_path, output_file_path):
        # Read the file content
        with open(input_file_path, 'r') as file:
            lines = file.readlines()

        # Fix lines with issues such as extra commas, incorrect quoting, etc.
        cleaned_lines = []
        for line in lines:
            # Replace triple quotes with single quotes
            line = re.sub(r'""+', '"', line)
            # Fix numbers with commas (e.g., "1,06E+00" to "1.06E+00")
            line = re.sub(r'(\d),(\d)', r'\1.\2', line)
            cleaned_lines.append(line)

        # Join cleaned lines back into a single string
        cleaned_content = ''.join(cleaned_lines)

        # Convert the cleaned string to a pandas DataFrame
        from io import StringIO
        df = pd.read_csv(StringIO(cleaned_content), sep=',', quotechar='"', encoding_errors='ignore')

        # Save the DataFrame to the specified output path
        df.to_csv(output_file_path, index=False)
        print(f"Cleaned CSV has been saved to {output_file_path}")



if __name__ == '__main__':
    path = '/Users/apple/PycharmProjects/pdf_server_2.1/core/server/inference_results/www.environdec.com:library:epd15790/csv/9425c71a42bab5d439e05b82fe5a85221ced3f0e3b69497cea51275df8458857.csv'
    csv = CsvReformat(csv_path=path)
    csv.apply_csv_reformat('/Users/apple/PycharmProjects/pdf_server_2.1/try')