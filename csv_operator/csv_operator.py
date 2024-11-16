import os
import re
import sys
import pandas as pd
from log.log import logger
from tqdm import tqdm
from tools import DeeplTranslate
from config.default import Default


# from config.core_default import CoreDefault


class CsvOperator:

    def __init__(self, factor_information=None, emission_factor=None, factor_property=None, property_management=None):
        self.factor_info_df = factor_information
        self.emission_df = emission_factor
        self.factor_prop_df = factor_property
        self.property_management_df = property_management
        self.dropped_ids = []
        self.tonne_ids = []
        self.output_path = None
        self.default = Default()

    # def load_csv(self, factor_information_path, emission_factor_path, factor_property_path, property_management_path):
    #     self.factor_info_df = pd.DataFrame()
    #     self.emission_df = pd.DataFrame()
    #     self.factor_prop_df = pd.DataFrame()
    #     self.property_management_df = pd.DataFrame()
    #
    #     if os.path.getsize(factor_information_path) > 0:
    #         self.factor_info_df = pd.read_csv(factor_information_path)
    #     if os.path.getsize(emission_factor_path) > 0:
    #         self.emission_df = pd.read_csv(emission_factor_path)
    #     if os.path.getsize(factor_property_path) > 0:
    #         self.factor_prop_df = pd.read_csv(factor_property_path)
    #     if os.path.getsize(property_management_path) > 0:
    #         self.property_management_df = pd.read_csv(property_management_path)

    def load_csv(self, factor_information_path, emission_factor_path, factor_property_path, property_management_path):
        self.factor_info_df = self.safe_read_csv(factor_information_path, self.default.factor_info_columns_sequence)
        self.emission_df = self.safe_read_csv(emission_factor_path, self.default.emission_factor_columns_sequence)
        self.factor_prop_df = self.safe_read_csv(factor_property_path, self.default.factor_properties_columns_sequence)
        self.property_management_df = self.safe_read_csv(property_management_path,
                                                         self.default.property_management_columns_sequence)

    def safe_read_csv(self, path, default_sequence):
        # Check if the file is empty or contains only empty rows
        with open(path, 'r') as f:
            first_non_empty_line = next((line for line in f if line.strip()), None)
            if not first_non_empty_line:
                return pd.DataFrame(
                    columns=default_sequence)  # Return an empty DataFrame if the file has only empty lines or is empty
        # If there is data, read the CSV
        return pd.read_csv(path)

    # Modifies: remove the duplicate column in factor_information

    def remove_duplicate(self):
        df = self.factor_info_df
        duplicate_rows = df[df.duplicated(subset='source_url', keep='first')]
        # try:
        #     self.dropped_ids
        # except NameError:
        #     self.dropped_ids = []

        self.dropped_ids.extend(duplicate_rows['id'].tolist())
        # df_unique = df.drop_duplicates(subset='source_url').reset_index(drop=True)

    def remove_null_gwp(self):
        df = self.emission_df
        missing_gwp_rows = df[df['value'].isna()]
        self.dropped_ids.extend(missing_gwp_rows['factor_id'].tolist())
        # df_cleaned = df.dropna(subset=['gwp']).reset_index(drop=True)

    def remove_no_name(self):
        df = self.factor_info_df
        missing_name_row = df[df['name_en'].isna()]
        self.dropped_ids.extend(missing_name_row['id'].tolist())
        # df_cleaned = df.dropna(subset=['name_en']).reset_index(drop=True)

    def remove_no_unit(self):
        df = self.factor_info_df
        missing_unit_row = df[df['unit'].isna()]
        self.dropped_ids.extend(missing_unit_row['id'].tolist())

    def drop_rows_by_ids(self) -> pd.DataFrame:
        """
        Removes rows from the DataFrame where the 'id' is in the dropped_ids list.

        Parameters:
        df (pd.DataFrame): The DataFrame from which rows are to be removed.
        dropped_ids (list): The list of 'id's to be removed.

        Returns:
        pd.DataFrame: A new DataFrame with the specified rows removed.
        """
        # Remove rows where 'id' is in the dropped_ids list
        # df_filtered = df[~df['id'].isin(dropped_ids)].reset_index(drop=True)
        self.factor_info_df = self.factor_info_df[~self.factor_info_df['id'].isin(self.dropped_ids)].reset_index(
            drop=True)
        self.emission_df = self.emission_df[~self.emission_df['factor_id'].isin(self.dropped_ids)].reset_index(
            drop=True)
        self.factor_prop_df = self.factor_prop_df[~self.factor_prop_df['factor_id'].isin(self.dropped_ids)].reset_index(
            drop=True)

    def unit_format(self):
        df_1 = self.factor_info_df
        df_2 = self.factor_prop_df
        df_1['unit'] = df_1['unit'].apply(self.__extract_unit)
        df_2['unit'] = df_2['unit'].apply(self.__extract_unit)
        self.factor_info_df = df_1
        self.factor_prop_df = df_2

        # df_3 = self.property_management_df
        # df_3['property_unit'] = df_3['property_unit'].apply(self.__extract_unit)
        # self.property_management_df = df_3

    @staticmethod
    def __extract_unit(text):
        # Remove unnecessary text
        text = re.sub(r'[^\w²/]+', ' ', text)
        # Extract unit part only (remove unnecessary text)
        unit = re.search(r'[a-zA-Z²/]+', text)
        return unit.group(0) if unit else ''

    def tonne_operation(self):
        df = self.emission_df
        self.__record_tonne_list()
        df = df.apply(self.__update_values, axis=1)
        self.emission_df = df

    def __record_tonne_list(self):
        df = self.factor_info_df
        self.tonne_ids = df[df['unit'].isin(['tonne', 'ton'])]['id'].tolist()
        # print(self.tonne_ids)

    def __update_values(self, row):
        if row['factor_id'] in self.tonne_ids:
            row['value'] *= 1000
        return row

    def url_format(self):
        df = self.factor_info_df
        df['source_url'] = df['source_url'].apply(self.__modify_url)
        self.factor_info_df = df

    @staticmethod
    def __modify_url(url):
        url = url.replace(':', '/')  # Replace ':' with '/'
        url = 'https://' + url  # Add 'https://'
        url = url.replace('.pdf', '')  # Remove '.pdf'
        return url

    @staticmethod
    def translate_csv(file_path, word_in_en, word_in_ch):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        translator = DeeplTranslate('336b855b-0252-4180-89e2-db101a755079:fx')

        # Initialize progress bar
        pbar = tqdm(total=len(df))

        # Translate and update the DataFrame
        for i, row in df.iterrows():
            pbar.update(1)  # Update progress bar

            if row[word_in_en] and not pd.notnull(row[word_in_ch]):
                translated_value = translator.translate_ch(row[word_in_en])
                df.at[i, word_in_ch] = translated_value

            # Save the DataFrame every 10 rows
            if (i + 1) % 10 == 0:
                df.to_csv(file_path, index=False)

        # Save the final DataFrame
        df.to_csv(file_path, index=False)
        pbar.close()

    def output_csv(self):
        DIR = self.output_path
        csv_folder_path = os.path.join(DIR, 'csv_refine')
        if not os.path.exists(csv_folder_path):
            os.makedirs(csv_folder_path)
        self.factor_info_df.to_csv(os.path.join(csv_folder_path, 'factor_information.csv'), index=False)
        self.emission_df.to_csv(os.path.join(csv_folder_path, 'emission_factor.csv'), index=False)
        self.factor_prop_df.to_csv(os.path.join(csv_folder_path, 'factor_property.csv'), index=False)
        self.property_management_df.to_csv(os.path.join(csv_folder_path, 'property_management.csv'), index=False)

    def apply_all(self, factor_info_path, emission_path, factor_prop_path, property_management_path, output_path):
        self.output_path = output_path
        self.load_csv(factor_info_path, emission_path, factor_prop_path, property_management_path)
        self.remove_duplicate()
        self.remove_no_name()
        self.remove_no_unit()
        self.remove_null_gwp()
        self.drop_rows_by_ids()
        self.url_format()
        self.unit_format()
        self.tonne_operation()
        self.output_csv()

        factor_info_final_path = os.path.join(self.output_path, 'csv_refine', 'factor_information.csv')
        property_management_final_path = os.path.join(self.output_path, 'csv_refine', 'property_management.csv')
        try:
            self.translate_csv(property_management_final_path, 'property_symbol',
                               'property_name')
            self.translate_csv(factor_info_final_path, "name_en",
                               "name_zh")
        except Exception as e:
            logger.error(f"Warning: An error occurred - {e}. Use python CSV_Google.py -h for help.")
            sys.exit()


if __name__ == "__main__":
    csv_operator = CsvOperator()
    factor_info_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/csv/factor_information.csv'
    emission_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/csv/emission_factor.csv'
    factor_prop_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/csv/factor_properties.csv'
    property_management_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/csv/properties_management.csv'
    csv_operator.apply_all(factor_info_path, emission_path, factor_prop_path, property_management_path)
