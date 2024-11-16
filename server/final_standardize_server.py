from csv_operator.csv_operator import CsvOperator

if __name__ == "__main__":
    csv_operators = CsvOperator()
    factor_info_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result_2/csv/factor_information.csv'
    emission_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result_2/csv/emission_factor.csv'
    factor_prop_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result_2/csv/factor_properties.csv'
    property_management_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result_2/csv/properties_management.csv'
    output_path = '/Users/apple/PycharmProjects/pdf_server_2.1/result_2'
    csv_operators.apply_all(factor_info_path, emission_path, factor_prop_path, property_management_path, output_path)
