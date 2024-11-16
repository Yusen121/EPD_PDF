import re
import pandas as pd
from tools import CellOperator

class RowOperator:
    """
    Select logic:
    1. if there is gwp-total(case-insensitive) return true
    2. if there is gwptotal(case-insensitive) return true
    3. gwp, total in different cells, not other extra word like gwp_goo, total, return true
    """

    @staticmethod
    def check_indicator(row, indicator, check_columns_name=False):
        no_symbol_lower_case_indicator = CellOperator.lowercase_no_symbol(indicator)
        lower_case_indicator = CellOperator.lowercase_has_symbol(indicator)
        check_row = row.apply(lambda x: CellOperator.lowercase_has_symbol(str(x)) if pd.notna(x) else "")
        pattern = r'[-,.;:|\s]'
        indicator_part = re.split(pattern, lower_case_indicator)
        indicator_part_set = set(indicator_part)
        dif_cell_set = set()

        for cell in check_row:
            try:
                if cell:
                    cell_no_symbol = CellOperator.lowercase_no_symbol(cell)
                    parts = re.split(pattern, cell)
                    dif_cell_set.update(parts)

                    if cell_no_symbol == no_symbol_lower_case_indicator:
                        return True
                    if cell == lower_case_indicator:
                        return True
                    if set(parts) == set(indicator_part):
                        return True
            except Exception as e:
                print(f"Exception occurred while processing cell '{cell}': {e}")

        if dif_cell_set == indicator_part_set:
            return True

        if check_columns_name:
            column_names = row.index
            for col in column_names:
                col_name = CellOperator.lowercase_has_symbol(col)
                col_name_no_symbol = CellOperator.lowercase_no_symbol(col)

                if col_name_no_symbol == no_symbol_lower_case_indicator or col_name == lower_case_indicator:
                    return True
                col_parts = re.split(pattern, col_name)
                if set(col_parts) == indicator_part_set:
                    return True

        return False

if __name__ == "__main__":
    data = {
        'Column1': ['gwp-t', 'Product', 'Product components', 'gwptotal', 'gwp', 'GWP-tot'],
        'Column2': ['value.GWP.total', 'ComponentS', 'nn', 'd', 'total', 'nnn']
    }
    csv_path = '/Users/apple/PycharmProjects/EPDLibrary/server/output/pdf/fda24abc-944d-4ab7-ac19-874ea72fa197/standardize/table_page_7_table_1.csv'

    # df1 = pd.read_csv(csv_path)
    df1 = pd.DataFrame(data)

    contains_property_components = df1.apply(lambda row: RowOperator.check_indicator(row, 'GWP-tot', True), axis=1).any()

    df1['Has_Indicator'] = df1.apply(lambda row: RowOperator.check_indicator(row, 'GWP-tot', True), axis=1)
    print(df1)
    print(contains_property_components)

# import re
# import pandas as pd
# from tools import CellOperator
#
#
# class RowOperator:
#     """
#     Select logic:
#     1. if there is gwp-total(case-insensitive) return true
#     2. if there is gwptotal(case-insensitive) return true
#     3. gwp, total in different cells, not other extra word like gwp_goo, total, return true
#
#     """
#     # Todo: GWPT
#
#     @staticmethod
#     def check_indicator(row, indicator, check_columns_name=False):
#         # Todo:
#         no_symbol_lower_case_indicator = CellOperator.lowercase_no_symbol(indicator)
#         lower_case_indicator = CellOperator.lowercase_has_symbol(indicator)
#         check_row = row.apply(lambda x: CellOperator.lowercase_has_symbol(str(x)) if pd.notna(x) else "")
#         pattern = r'[-,.;:|\s]'
#         indicator_part = re.split(pattern, lower_case_indicator)
#         indicator_part_set = set(indicator_part)
#         dif_cell_set = set()
#
#         for cell in check_row:
#             try:
#                 if cell:
#                     cell = cell.replace(' ', '')
#                     parts = re.split(pattern, cell)
#                     dif_cell_set.update(parts)
#                     if cell == no_symbol_lower_case_indicator:
#                         return True
#                     if cell == lower_case_indicator:
#                         return True
#                     if set(parts) == set(indicator_part):
#                         return True
#             except Exception as e:
#                 print(f"Exception occurred while processing cell '{cell}': {e}")
#
#         if dif_cell_set == indicator_part_set:
#             return True
#
#         if check_columns_name:
#             column_names = row.index
#             for col in column_names:
#                 col_name = CellOperator.lowercase_has_symbol(col)
#                 if col_name == no_symbol_lower_case_indicator or col_name == lower_case_indicator:
#                     return True
#                 col_parts = re.split(pattern, col_name)
#                 if set(col_parts) == indicator_part_set:
#                     return True
#         return False
#
#
#
#
# if __name__ == "__main__":
#     data = {
#         'Column1': ['gwp-t', 'Product', 'Product components'],
#         'Column2': ['value.GWP.total', 'ComponentS', 'nn']
#     }
#     csv_path = '/Users/apple/PycharmProjects/EPDLibrary/server/output/pdf/0c32d23d-0daf-44bb-b245-fb17341bf51f/standardize/table_page_9_table_1.csv'
#
#     df1 = pd.read_csv(csv_path)
#     df = pd.DataFrame(data)
#
#     contains_property_components = df1.apply(lambda row:
#                                                  RowOperator.check_indicator(row, 'GWP-total [kg CO2 eq.]', True),
#                                                  axis=1).any()
#
#     df1['Has_Indicator'] = df1.apply(lambda row: RowOperator.check_indicator(row, 'GWP-total [kg CO2 eq.]', True), axis=1)
#     print(df1)
#     print(contains_property_components)
#
#
