import datetime
import os

import pandas as pd

from tools import SnowflakeIDGenerator
from tools import ColumnReformat
from config import Default
from core.extractor.text_extractor import TextExtractor
from core.extractor.table_extractor import TableExtractor




class CsvGenerator:
    def __init__(self, uuid, table_extractor: TableExtractor, text_extractor: TextExtractor, output_path, source_url):
        self.core_default = Default()
        self.columns_reformat = ColumnReformat()
        current_time = datetime.datetime.now()
        self.output_path = os.path.join(output_path, 'csv')
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # Objects
        self.snowflake_gen = SnowflakeIDGenerator(1, 1)
        # factor_info
        self.id = self.snowflake_gen.next_id()
        self.uuid = uuid
        self.name_zh = None
        self.name_en = text_extractor.get_name_en()
        if text_extractor.get_unit():
            self.unit = text_extractor.get_unit()
        else:
            self.unit = table_extractor.declared_unit
        self.sampling_start = text_extractor.get_sample_start()
        self.sampling_end = text_extractor.get_sample_end()
        self.valid_time = text_extractor.get_valid_time()
        self.location = text_extractor.get_location()
        self.class_code = None
        self.description = text_extractor.get_description()
        self.source_description = "The International EPD® System"
        self.source_original_id = None
        self.source_url = source_url
        self.classification_system = None
        self.source = 'EPD'
        self.source_type = 3
        self.completeness_type = 4
        self.first_class = None
        self.second_class = None
        self.third_class = None
        self.data_entry_by = "吴宇森"
        self.location_id = None
        self.synonyms = None
        self.data_version = None
        self.create_time = current_time
        self.class_id = None
        # Todo: gwp calculation
        # self.gwp_sum = self.__gwp_sum_calculation()

        # emission_factor
        self.gwp_a1_a3 = table_extractor.get_gwp_a1_a3()
        self.gwp_a4_a5 = table_extractor.get_gwp_a4_a5()
        self.gwp_b1_b7 = table_extractor.get_gwp_b1_b7()
        self.gwp_c1_c4 = table_extractor.get_gwp_c1_c4()
        self.gwp_d = table_extractor.get_gwp_d()

        # factor_property:
        self.property_unit = table_extractor.property_unit
        self.property_list = table_extractor.property_list
        self.property_list_ai = table_extractor.property_list_2

        # property_management:

        # load csv
        self.df = None
        self.df_emission = None
        self.df_factor_properties = None
        self.df_properties_management = None

        self.__load_factor_information()
        self.__load_emission_factor()
        self.__load_factor_properties()
        self.__load_properties_management()

    def generate_csv(self):
        self.__generate_factor_information_csv()
        self.__generate_emission_factor_csv()
        self.__generate_factor_properties_csv()
        self.__generate_property_management_csv()

    def __load_factor_information(self):
        file_path = os.path.join(self.output_path, 'factor_information.csv')
        if os.path.exists(file_path):
            self.df = pd.read_csv(file_path)
        else:
            self.df = pd.DataFrame(columns=self.core_default.factor_info_columns_sequence)

    def __load_emission_factor(self):
        file_path = os.path.join(self.output_path, 'emission_factor.csv')
        if os.path.exists(file_path):
            self.df_emission = pd.read_csv(file_path)
        else:
            self.df_emission = pd.DataFrame(columns=self.core_default.emission_factor_columns_sequence)

    def __load_factor_properties(self):
        file_path = os.path.join(self.output_path, 'factor_properties.csv')
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                self.df_factor_properties = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                self.df_factor_properties = pd.DataFrame(columns=self.core_default.factor_properties_columns_sequence)
        else:
            self.df_factor_properties = pd.DataFrame(columns=self.core_default.factor_properties_columns_sequence)

    def __load_properties_management(self):
        file_path = os.path.join(self.output_path, 'properties_management.csv')
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                self.df_properties_management = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                self.df_properties_management = pd.DataFrame(
                    columns=self.core_default.property_management_columns_sequence)
        else:
            self.df_properties_management = pd.DataFrame(columns=self.core_default.property_management_columns_sequence)
    # def __load_properties_management(self):
    #     file_path = os.path.join(self.output_folder_path, 'properties_management.csv')
    #     if os.path.exists(file_path):
    #         self.df_properties_management = pd.read_csv(file_path)
    #     else:
    #         self.df_properties_management = pd.DataFrame(columns=self.core_default.property_management_columns_sequence)

    def __generate_factor_information_csv(self):
        df = pd.DataFrame(
            {
                'id': [self.id],
                'uuid': [self.uuid],
                'name_zh': [self.name_zh],
                'name_en': [self.name_en],
                'unit': [self.unit],
                'sampling_start': [self.sampling_start],
                'sampling_end': [self.sampling_end],
                'valid_time': [self.valid_time],
                # Two Level
                'location': [self.location],
                'class_code': [self.class_code],
                # Editing
                'description': [self.description],
                'source_description': [self.source_description],
                'source_original_id': self.source_original_id,
                'source_url': [self.source_url],
                # Normal
                'classification_system': self.classification_system,
                'source': self.source,
                'source_type': self.source_type,
                'completeness_type': self.completeness_type,
                # Judge
                'first_class': self.first_class,
                'second_class': self.second_class,
                'third_class': self.third_class,
                'data_entry_by': self.data_entry_by,
                'location_id': self.location_id,
                'synonyms': self.synonyms,
                'data_version': self.data_version,
                "create_time": self.create_time
            }
        )
        self.columns_reformat.factor_info_columns_rearrange(df)
        df = self.__concat_df(self.df, df)
        output_file = os.path.join(self.output_path, 'factor_information.csv')
        df.to_csv(output_file, index=False)

    def __generate_emission_factor_csv(self):
        if self.unit == 't':
            value_a1_a2_a3 = (self.gwp_a1_a3 or 0) * 1000
            value_a4_a5 = (self.gwp_a4_a5 or 0) * 1000
            value_b1_b7 = (self.gwp_b1_b7 or 0) * 1000
            value_c1_c4 = (self.gwp_c1_c4 or 0) * 1000
            value_d = (self.gwp_d or 0) * 1000
        else:
            value_a1_a2_a3 = self.gwp_a1_a3
            value_a4_a5 = self.gwp_a4_a5
            value_b1_b7 = self.gwp_b1_b7
            value_c1_c4 = self.gwp_c1_c4
            value_d = self.gwp_d
        emission_data = (
            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_a1_a2_a3,
                'ghg_type': 'CO2',
                'boundary': 'A1-A3',
                'formula': None,
                'description': None
            } if value_a1_a2_a3 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_a1_a2_a3,
                'ghg_type': 'Total',
                'boundary': 'A1-A3',
                'formula': None,
                'description': None
            } if value_a1_a2_a3 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_a4_a5,
                'ghg_type': 'CO2',
                'boundary': 'A4-A5',
                'formula': None,
                'description': None
            } if value_a4_a5 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_a4_a5,
                'ghg_type': 'Total',
                'boundary': 'A4-A5',
                'formula': None,
                'description': None
            } if value_a4_a5 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_b1_b7,
                'ghg_type': 'CO2',
                'boundary': 'B1-B7',
                'formula': None,
                'description': None
            } if value_b1_b7 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_b1_b7,
                'ghg_type': 'Total',
                'boundary': 'B1-B7',
                'formula': None,
                'description': None
            } if value_b1_b7 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_c1_c4,
                'ghg_type': 'CO2',
                'boundary': 'C1-C4',
                'formula': None,
                'description': None
            } if value_c1_c4 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_c1_c4,
                'ghg_type': 'Total',
                'boundary': 'C1-C4',
                'formula': None,
                'description': None
            } if value_c1_c4 != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_d,
                'ghg_type': 'CO2',
                'boundary': 'D',
                'formula': None,
                'description': None
            } if value_d != 0 else None,

            {
                'id': self.snowflake_gen.next_id(),
                'factor_id': self.id,
                'uuid': self.uuid,
                'value': value_d,
                'ghg_type': 'Total',
                'boundary': 'D',
                'formula': None,
                'description': None
            } if value_d != 0 else None,
        )
        emission_data = [entry for entry in emission_data if entry is not None]
        new_emission = pd.DataFrame(emission_data, columns=self.core_default.emission_factor_columns_sequence)
        df_emission = self.__concat_df(self.df_emission, new_emission)
        output_file = os.path.join(self.output_path, 'emission_factor.csv')
        df_emission.to_csv(output_file, index=False)

    # Todo: snow_id not working
    def __generate_factor_properties_csv(self):
        properties_list_ai = self.property_list_ai
        df = None
        if properties_list_ai:
            snowflake_gen_1 = SnowflakeIDGenerator(datacenter_id=2, worker_id=2)
            df = pd.DataFrame(properties_list_ai, columns=['property_name', 'property_value', 'unit'])
            df['factor_id'] = str(self.id)
            df['data_entry_by'] = '吴宇森'
            df['id'] = [str(snowflake_gen_1.next_id()) for _ in range(len(df))]
        else:
            df = pd.DataFrame(columns=self.core_default.factor_properties_columns_sequence)

        # """
        # Method 2
        # Creates a CSV file from the given list of strings, including a unit column.
        #
        # Args:
        #     input_list (list): A list of strings in the format "Property: Value".
        #     unit (str): The unit to be added for each property.
        #     output_file (str): The path to the output CSV file.
        # """
        # # Split each string into property_name and value
        # input_list = self.property_list
        # unit = self.property_unit
        # if input_list:
        #     data = [item.split(": ") for item in input_list]
        #     factor_id = self.id
        #     formular = None
        #     description = None
        #
        #     # Add the unit to each entry
        #     data_with_units = [item + [unit, self.snowflake_gen.next_id(),
        #                                factor_id, self.data_entry_by, formular, description] for item in data]
        #
        #     # Create a DataFrame
        #     df = pd.DataFrame(data_with_units, columns=['property_name', 'property_value', 'unit', 'id', 'factor_id',
        #                                                 'data_entry_by', 'formula', 'description'])


        # Save DataFrame to CSV
        new_factor_properties = pd.DataFrame(df, columns=self.core_default.factor_properties_columns_sequence)

        df_factor_properties = self.__concat_df(self.df_factor_properties, new_factor_properties)
        output_file = os.path.join(self.output_path, 'factor_properties.csv')
        df_factor_properties.to_csv(output_file, index=False)

    def __generate_property_management_csv(self):
        # Method 1
        properties_list_ai = self.property_list_ai
        df = None
        if properties_list_ai:
            snowflake_gen_1 = SnowflakeIDGenerator(datacenter_id=2, worker_id=2)
            df = pd.DataFrame(properties_list_ai, columns=['property_symbol', 'property_value', 'property_unit'])
            df['data_entry_by'] = '吴宇森'
            df['id'] = [str(snowflake_gen_1.next_id()) for _ in range(len(df))]
        else:
            df = pd.DataFrame(columns=self.core_default.property_management_columns_sequence)

        # Method 2
        # input_list = self.property_list

        # if input_list:
        #     unit = self.property_unit
        #     data_entry_by = self.data_entry_by
        #     property_name = None
        #     description = None
        #     new_data = [[item.split(": ")[0], unit, self.snowflake_gen.next_id(), data_entry_by, property_name,
        #                  description] for item in input_list]
        #
        #     df = pd.DataFrame(new_data, columns=['property_symbol', 'property_unit',
        #                                          'id', 'data_entry_by', 'property_name',
        #                                          'description'])
        df = pd.DataFrame(df, columns=self.core_default.property_management_columns_sequence)
        df_properties_management = self.__concat_df(self.df_properties_management, df)
        df_properties_management = df_properties_management.drop_duplicates(
            subset=["property_symbol", "property_unit"],
            keep='first')

        output_file = os.path.join(self.output_path, 'properties_management.csv')
        df_properties_management.to_csv(output_file, index=False)

    @staticmethod
    def __concat_df(df_self, df):
        if not df_self.empty and not df.empty:
            df = pd.concat([df_self, df], axis=0)
        elif not df_self.empty:
            df = df_self.copy()
        elif not df.empty:
            df = df.copy()
        else:
            df = pd.DataFrame()
        return df
