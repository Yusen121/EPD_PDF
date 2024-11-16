from pathlib import Path


class Default:
    def __init__(self):
        self.standardize_folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/standardize'
        self.single_epd_path = '/Users/apple/PycharmProjects/EPDLibrary/data/input/epd_1.pdf'
        self.single_pdf_output_folder_path = '/Users/apple/PycharmProjects/EPDLibrary/data/output/split_method'
        self.api_key = 'sk-54883113c80444b9aae8d40cfdf7f98b'

        self.factor_info_columns_sequence = [
            'id', 'uuid', 'name_zh', 'name_en', 'unit', 'location', 'location_id', 'sampling_start', 'sampling_end',
            'valid_time', 'description', 'source', 'source_original_id', 'source_description',
            'source_url', 'source_type', 'completeness_type', 'data_version',
            'data_entry_by', 'classification_system', 'synonyms', 'class_id',
            'first_class', 'second_class', 'third_class', 'create_time'
        ]

        self.emission_factor_columns_sequence = ['id', 'factor_id', 'uuid',
                                                 'value', 'ghg_type', 'boundary',
                                                 'formula', 'description']

        self.factor_properties_columns_sequence = ['id', 'factor_id', 'property_name',
                                                   'property_value', 'unit', 'description',
                                                   'data_entry_by', 'formula']

        self.property_management_columns_sequence = ['id', 'property_name', 'property_symbol',
                                                     'property_unit', 'description',
                                                     'data_entry_by']
        self.magic_pdf_path = Path('/Users/apple/PycharmProjects/pdf_server_2.1/result/magic-pdf')

