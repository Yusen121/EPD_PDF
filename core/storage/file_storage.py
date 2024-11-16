import os
from config import Default


class FileStorage:
    default = Default()

    def __init__(self):
        pass

    @staticmethod
    def file_storage_executor(output_path):
        output_folder_path = os.path.join(output_path, 'pdf_output')

    # Todo: if there is no standardize folder, create it
    @staticmethod
    def standardize_storage(df, name, output_path):
        standardize_path = os.path.join(output_path, name)
        df.to_csv(standardize_path, index=False)


if __name__ == '__main__':
    # Example usage:
    import pandas as pd

    example_data = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(example_data)
    file_storage = FileStorage()
    file_storage.standardize_storage(df, 'example.csv')
