import ast
import os
import re
import numpy as np
import pandas as pd
from log.log import logger
from core.extractor.text_extractor import TextExtractor
from core.extractor.ai_extractor import AiExtractor
from tools import TableCleaning, CellOperator
from tools.row_operator import RowOperator


class TableExtractor:
    table_cleaning = TableCleaning

    def __init__(self):
        self.df = None
        self.gwp_df = None
        self.factor_properties_df = None
        self.property_unit = None
        self.property_list = None
        self.property_list_2 = None
        self.declared_unit = None

        self.gwp_a1_a3 = None
        self.gwp_a4_a5 = None
        self.gwp_b1_b7 = None
        self.gwp_c1_c4 = None
        self.gwp_d = None

    def load_csv(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def __load_df(self, df):
        self.df = df

    def show_value(self):
        # print('property unit is ' + str(self.property_unit))
        print('property list is ' + str(self.property_list_2))
        print('gwp value for a1-a3 is ' + str(self.gwp_a1_a3))
        print('gwp value for a4-a5 is ' + str(self.gwp_a4_a5))
        print('gwp value for b1-b7 is ' + str(self.gwp_b1_b7))
        print('gwp value for c1-c4 is ' + str(self.gwp_c1_c4))
        print('gwp value for d is ' + str(self.gwp_d))
        if self.declared_unit:
            print('declare unit is' + str(self.declared_unit))

    def multiple_dfs_extracts(self, dfs: list):
        for df in dfs:
            try:
                self.__load_df(df)
                self.extract_gwp()
                self.extract_property()
                self.extract_declare_unit()
            except Exception as e:
                print(f'{e}, the error df is {df}')
                continue

    def multiple_csvs_extracts(self, folder_path: str):
        # Get all CSV files in the folder
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

        for csv_file in csv_files:
            csv_path = os.path.join(folder_path, csv_file)
            try:
                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_path)
                # Process the DataFrame
                self.__load_df(df)
                self.extract_gwp()
                self.extract_property()
                self.extract_declare_unit()
                if self.gwp_a1_a3 is None and self.gwp_a4_a5 is None and self.gwp_b1_b7 is None and self.gwp_c1_c4 is None and self.gwp_d is None:
                    logger.info(f'There is no gwp value, the folder path of it is {folder_path}')
            except Exception as e:
                logger.error(f'{e}, the error file is {csv_file}, in this folder {folder_path}')
                continue

    def extract_declare_unit(self):
        if self.is_declare_unit():
            unit_df = self.df[self.df.apply(lambda row: RowOperator.check_indicator(row, 'declare-unit'),
                                            axis=1)]
            if unit_df.empty:
                unit_df = self.column_name_row_to_df(unit_df)
            requirement = ("Get the declare unit of product in the dataframe, "
                           "give me only the declared unit using this format: Declared Unit: kg,"
                           "For example:"
                           "remember, only the mathematical unit, not other description"
                           "kg is an example")
            ai_extractor_unit = AiExtractor(unit_df)
            result = ai_extractor_unit.csv_requirement(requirement)
            if TextExtractor.result_unit(result):
                self.declared_unit = TextExtractor.result_unit(result)

    @staticmethod
    def column_name_row_to_df(df):
        df.loc[0] = df.columns
        df.columns = [f'column{i + 1}' for i in range(len(df.columns))]
        return df

    def is_declare_unit(self):
        contains_declare_unit_1 = self.df.apply(lambda row: RowOperator.check_indicator(row, 'declare-unit',
                                                                                        True),
                                                axis=1).any()
        contains_declare_unit_2 = self.df.apply(lambda row: RowOperator.check_indicator(row, 'declared-unit',
                                                                                        True),
                                                axis=1).any()
        return contains_declare_unit_1 or contains_declare_unit_2

    def extract_gwp(self):
        self.apply_greek_with_english_to_dataframe()
        # if self.__check_gwp_value() and self.is_boundary_in_df():
        if self.__check_gwp_value():
            is_boundary = self.is_boundary_in_df()
            # if is_boundary:
            #     print('There is a boundary!!!!')
            # else:
            #     print('No boundary')
            if self.is_boundary_in_df():
                self.gwp_df = self.find_and_filter_rows()
                self.get_gwp_value_from_df()
                return self.gwp_df

    def __check_gwp_value(self):
        contains_gwp_total = self.df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-total'),
                                           axis=1).any()
        contains_gwp_t = self.df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-t'),
                                       axis=1).any()
        contains_gwp_tot = self.df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-tot'),
                                         axis=1).any()
        contains_gwp_tot_unit_1 = self.df.apply(lambda row: RowOperator.check_indicator(row,
                                                                                        'GWP-total [kg CO2 eq.]'),
                                                axis=1).any()
        contains_gwp_tot_unit_2 = self.df.apply(lambda row: RowOperator.check_indicator(row,
                                                                                        'GWP-totale'),
                                                axis=1).any()
        contains_gwp_tot_unit_3 = self.df.apply(lambda row:
                                                RowOperator.check_indicator(row,
                                                                            'GlobalWarmingPotential-Total'),
                                                axis=1).any()
        return contains_gwp_total or contains_gwp_t or contains_gwp_tot or contains_gwp_tot_unit_1 or contains_gwp_tot_unit_2 or contains_gwp_tot_unit_3

    def find_and_filter_rows(self):
        df = self.df
        # df = df.applymap(self.replace_greek_with_english)
        boundary_to_find = ['A1', 'A2', 'A3', 'A4', 'A5', 'A1-A3', 'A4-A5',
                            'B1-B7', 'C1', 'C2', 'C3', 'C4', 'D']
        df = self.replace_column_names_with_boundary_row(df, boundary_to_find)

        gwp_df = df[df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-total'), axis=1)]

        if gwp_df.empty:
            gwp_df = df[df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-t'), axis=1)]
            if gwp_df.empty:
                gwp_df = df[df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-tot'), axis=1)]
                if gwp_df.empty:
                    gwp_df = df[df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-total [kg CO2 eq.]'),
                                         axis=1)]
                    if gwp_df.empty:
                        gwp_df = df[df.apply(lambda row: RowOperator.check_indicator(row, 'GWP-totale'),
                                             axis=1)]
                        if gwp_df.empty:
                            gwp_df = df[
                                df.apply(lambda row: RowOperator.check_indicator(row, 'GlobalWarmingPotential-Total'),
                                         axis=1)]
                            if gwp_df.empty:
                                raise ValueError('No gwp value found')

        return gwp_df

    def is_boundary_in_df(self):
        boundary_to_find = ['A1', 'A2', 'A3', 'A4', 'A5', 'A1-A3', 'A4-A5',
                            'B1-B7', 'C1', 'C2', 'C3', 'C4', 'D']

        df = self.df

        # Check in columns
        for boundary in boundary_to_find:
            if boundary in df.columns:
                return True

        # Check in cells
        for boundary in boundary_to_find:
            if df.isin([boundary]).any().any():
                return True
        return False

    @staticmethod
    def replace_greek_with_english(text):
        greek_to_english = {
            'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z',
            'Η': 'H', 'Θ': 'Th', 'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M',
            'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Π': 'P', 'Ρ': 'R', 'Σ': 'S',
            'Τ': 'T', 'Υ': 'Y', 'Φ': 'Ph', 'Χ': 'Ch', 'Ψ': 'Ps', 'Ω': 'O'
        }

        for greek, english in greek_to_english.items():
            text = text.replace(greek, english)
        return text

    def apply_greek_with_english_to_dataframe(self):
        self.df.columns = [self.replace_greek_with_english(col) for col in self.df.columns]
        self.df = self.df.applymap(lambda x: self.replace_greek_with_english(x) if isinstance(x, str) else x)

    @staticmethod
    def replace_column_names_with_boundary_row(df, boundary_to_find):
        # Iterate over each row
        for index, row in df.iterrows():
            # Check if any value in the row matches the boundary values
            if any(cell in boundary_to_find for cell in row):
                # Replace the column names with the values in the found row
                df.columns = row
                # Drop the row used to set column names
                df = df.drop(index)
                break
        return df

    def convert_to_float(self, value):
        try:
            if value:
                if isinstance(value, (list, np.ndarray)):
                    value = value[0]
                    value = str(value).replace(',', '.')
                    return float(value)
                if isinstance(value, (int, float)):
                    value = str(value).replace(',', '.')
                    return float(value)
                elif isinstance(value, str):
                    value = value.replace(',', '.')
                    return float(value)
                else:
                    raise ValueError("Invalid value type")
            return 0

        except ValueError as e:
            print(f"Exception occurred while processing value '{value}': {e}")
            # Return 0 here after logging the exception
            return 0


    def get_gwp_value_from_df(self, indicator='GWP-total'):
        gwp_df = self.gwp_df

        # Replace Greek characters with English characters in column names and convert to lowercase
        gwp_df.columns = (gwp_df.columns
                          .str.replace('Α', 'A', case=False)
                          .str.replace('Β', 'B', case=False)
                          .str.replace('C', 'C', case=False)
                          .str.replace('D', 'D', case=False)
                          .str.replace(' ', '')
                          .str.lower())  # Convert all column names to lowercase

        columns = gwp_df.columns
        try:
            if "a1-a3" in columns:
                gwp_a1_a3_new = gwp_df["a1-a3"].values[0]
                if isinstance(gwp_a1_a3_new, str):
                    gwp_a1_a3 = gwp_a1_a3_new.replace(" ", "")
                else:
                    gwp_a1_a3 = gwp_a1_a3_new
                gwp_a1_a3_float = self.convert_to_float(gwp_a1_a3)
                self.gwp_a1_a3 = gwp_a1_a3_float
            else:
                a1_value = self.convert_to_float(
                    gwp_df["a1"].values[0].replace(" ", "") if isinstance(gwp_df["a1"].values[0], str) else
                    gwp_df["a1"].values[0]
                ) if "a1" in gwp_df.columns else 0.0

                a2_value = self.convert_to_float(
                    gwp_df["a2"].values[0].replace(" ", "") if isinstance(gwp_df["a2"].values[0], str) else
                    gwp_df["a2"].values[0]
                ) if "a2" in gwp_df.columns else 0.0

                a3_value = self.convert_to_float(
                    gwp_df["a3"].values[0].replace(" ", "") if isinstance(gwp_df["a3"].values[0], str) else
                    gwp_df["a3"].values[0]
                ) if "a3" in gwp_df.columns else 0.0

                # a1_value = self.convert_to_float(
                #     gwp_df["a1"].values[0].replace(" ", "")) if "a1" in gwp_df.columns else 0.0
                # a2_value = self.convert_to_float(
                #     gwp_df["a2"].values[0].replace(" ", "")) if "a2" in gwp_df.columns else 0.0
                # a3_value = self.convert_to_float(
                #     gwp_df["a3"].values[0].replace(" ", "")) if "a3" in gwp_df.columns else 0.0
                self.gwp_a1_a3 = a1_value + a2_value + a3_value
            print("Processed A1-A3 values")

            if "a4-a5" in columns:
                self.gwp_a4_a5 = self.convert_to_float(
                    gwp_df["a4-a5"].values[0].replace(" ", "") if isinstance(gwp_df["a4-a5"].values[0], str) else
                    gwp_df["a4-a5"].values[0]
                )

                # self.gwp_a4_a5 = self.convert_to_float(gwp_df["a4-a5"].values[0].replace(" ", ""))
            else:
                a4_value = self.convert_to_float(
                    gwp_df["a4"].values[0].replace(" ", "") if isinstance(gwp_df["a4"].values[0], str) else
                    gwp_df["a4"].values[0]
                ) if "a4" in gwp_df.columns else 0.0

                a5_value = self.convert_to_float(
                    gwp_df["a5"].values[0].replace(" ", "") if isinstance(gwp_df["a5"].values[0], str) else
                    gwp_df["a5"].values[0]
                ) if "a5" in gwp_df.columns else 0.0

                self.gwp_a4_a5 = a4_value + a5_value

                # a4_value = self.convert_to_float(
                #     gwp_df["a4"].values[0].replace(" ", "")) if "a4" in gwp_df.columns else 0.0
                # a5_value = self.convert_to_float(
                #     gwp_df["a5"].values[0].replace(" ", "")) if "a5" in gwp_df.columns else 0.0
                # self.gwp_a4_a5 = a4_value + a5_value
            print("Processed A4-A5 values")

            if "b1-b7" in columns:
                self.gwp_b1_b7 = self.convert_to_float(
                    gwp_df["b1-b7"].values[0].replace(" ", "") if isinstance(gwp_df["b1-b7"].values[0], str) else
                    gwp_df["b1-b7"].values[0]
                )
                # self.gwp_b1_b7 = self.convert_to_float(gwp_df["b1-b7"].values[0].replace(" ", ""))
            else:
                b1_value = self.convert_to_float(
                    gwp_df["b1"].values[0].replace(" ", "") if isinstance(gwp_df["b1"].values[0], str) else
                    gwp_df["b1"].values[0]
                ) if "b1" in gwp_df.columns else 0.0

                b2_value = self.convert_to_float(
                    gwp_df["b2"].values[0].replace(" ", "") if isinstance(gwp_df["b2"].values[0], str) else
                    gwp_df["b2"].values[0]
                ) if "b2" in gwp_df.columns else 0.0

                b3_value = self.convert_to_float(
                    gwp_df["b3"].values[0].replace(" ", "") if isinstance(gwp_df["b3"].values[0], str) else
                    gwp_df["b3"].values[0]
                ) if "b3" in gwp_df.columns else 0.0

                b4_value = self.convert_to_float(
                    gwp_df["b4"].values[0].replace(" ", "") if isinstance(gwp_df["b4"].values[0], str) else
                    gwp_df["b4"].values[0]
                ) if "b4" in gwp_df.columns else 0.0

                b5_value = self.convert_to_float(
                    gwp_df["b5"].values[0].replace(" ", "") if isinstance(gwp_df["b5"].values[0], str) else
                    gwp_df["b5"].values[0]
                ) if "b5" in gwp_df.columns else 0.0

                b6_value = self.convert_to_float(
                    gwp_df["b6"].values[0].replace(" ", "") if isinstance(gwp_df["b6"].values[0], str) else
                    gwp_df["b6"].values[0]
                ) if "b6" in gwp_df.columns else 0.0

                b7_value = self.convert_to_float(
                    gwp_df["b7"].values[0].replace(" ", "") if isinstance(gwp_df["b7"].values[0], str) else
                    gwp_df["b7"].values[0]
                ) if "b7" in gwp_df.columns else 0.0

                # b1_value = self.convert_to_float(
                #     gwp_df["b1"].values[0].replace(" ", "")) if "b1" in gwp_df.columns else 0.0
                # b2_value = self.convert_to_float(
                #     gwp_df["b2"].values[0].replace(" ", "")) if "b2" in gwp_df.columns else 0.0
                # b3_value = self.convert_to_float(
                #     gwp_df["b3"].values[0].replace(" ", "")) if "b3" in gwp_df.columns else 0.0
                # b4_value = self.convert_to_float(
                #     gwp_df["b4"].values[0].replace(" ", "")) if "b4" in gwp_df.columns else 0.0
                # b5_value = self.convert_to_float(
                #     gwp_df["b5"].values[0].replace(" ", "")) if "b5" in gwp_df.columns else 0.0
                #
                # # b6_value = self.convert_to_float(
                # #     gwp_df["b6"].values[0].replace(" ", "")) if "b6" in gwp_df.columns else 0.0
                # gwp_b6 = gwp_df["b6"].values[0].replace(" ", "")
                # b6_value = self.convert_to_float(gwp_b6) if "b6" in gwp_df.columns else 0.0
                #
                # b7_value = self.convert_to_float(
                #     gwp_df["b7"].values[0].replace(" ", "")) if "b7" in gwp_df.columns else 0.0
                self.gwp_b1_b7 = b1_value + b2_value + b3_value + b4_value + b5_value + b6_value + b7_value
            print("Processed B1-B7 values")

            if "c1-c4" in columns:
                self.gwp_c1_c4 = self.convert_to_float(
                    gwp_df["c1-c4"].values[0].replace(" ", "") if isinstance(gwp_df["c1-c4"].values[0], str) else
                    gwp_df["c1-c4"].values[0]
                )

                # self.gwp_c1_c4 = self.convert_to_float(gwp_df["c1-c4"].values[0].replace(" ", ""))
            else:
                c1_value = self.convert_to_float(
                    gwp_df["c1"].values[0].replace(" ", "") if isinstance(gwp_df["c1"].values[0], str) else
                    gwp_df["c1"].values[0]
                ) if "c1" in gwp_df.columns else 0.0

                c2_value = self.convert_to_float(
                    gwp_df["c2"].values[0].replace(" ", "") if isinstance(gwp_df["c2"].values[0], str) else
                    gwp_df["c2"].values[0]
                ) if "c2" in gwp_df.columns else 0.0

                c3_value = self.convert_to_float(
                    gwp_df["c3"].values[0].replace(" ", "") if isinstance(gwp_df["c3"].values[0], str) else
                    gwp_df["c3"].values[0]
                ) if "c3" in gwp_df.columns else 0.0

                c4_value = self.convert_to_float(
                    gwp_df["c4"].values[0].replace(" ", "") if isinstance(gwp_df["c4"].values[0], str) else
                    gwp_df["c4"].values[0]
                ) if "c4" in gwp_df.columns else 0.0

                self.gwp_c1_c4 = c1_value + c2_value + c3_value + c4_value

                # c1_value = self.convert_to_float(
                #     gwp_df["c1"].values[0].replace(" ", "")) if "c1" in gwp_df.columns else 0.0
                # c2_value = self.convert_to_float(
                #     gwp_df["c2"].values[0].replace(" ", "")) if "c2" in gwp_df.columns else 0.0
                # c3_value = self.convert_to_float(
                #     gwp_df["c3"].values[0].replace(" ", "")) if "c3" in gwp_df.columns else 0.0
                # c4_value = self.convert_to_float(
                #     gwp_df["c4"].values[0].replace(" ", "")) if "c4" in gwp_df.columns else 0.0
                # self.gwp_c1_c4 = c1_value + c2_value + c3_value + c4_value
            print("Processed C1-C4 values")

            if "d" in columns:
                self.gwp_d = self.convert_to_float(
                    gwp_df["d"].values[0].replace(" ", "") if isinstance(gwp_df["d"].values[0], str) else
                    gwp_df["d"].values[0]
                )

                # self.gwp_d = self.convert_to_float(gwp_df["d"].values[0].replace(" ", ""))
            else:
                self.gwp_d = 0.0
            print("Processed D values")

        except Exception as e:
            print(f"An error occurred: {e}")

    # def get_gwp_value_from_df(self, indicator='GWP-total'):
    #     gwp_df = self.gwp_df
    #
    #     # Replace Greek characters with English characters in column names and convert to lowercase
    #     gwp_df.columns = (gwp_df.columns
    #                       .str.replace('Α', 'A', case=False)
    #                       .str.replace('Β', 'B', case=False)
    #                       .str.replace('C', 'C', case=False)
    #                       .str.replace('D', 'D', case=False)
    #                       .str.replace(' ', '')
    #                       .str.lower())  # Convert all column names to lowercase
    #     columns = gwp_df.columns
    #     if "a1-a3" in columns:
    #         gwp_a1_a3 = gwp_df["a1-a3"].values[0].replace(" ", "")
    #         gwp_a1_a3_float = self.convert_to_float(gwp_a1_a3)
    #         # self.gwp_a1_a3 = self.__convert_to_float(gwp_df["a1-a3"].values[0])
    #         self.gwp_a1_a3 = gwp_a1_a3_float
    #     else:
    #         a1_value = self.convert_to_float(gwp_df["a1"].values[0].replace(" ", "")) if "a1" in gwp_df.columns else 0.0
    #         a2_value = self.convert_to_float(gwp_df["a2"].values[0].replace(" ", "")) if "a2" in gwp_df.columns else 0.0
    #         a3_value = self.convert_to_float(gwp_df["a3"].values[0].replace(" ", "")) if "a3" in gwp_df.columns else 0.0
    #         self.gwp_a1_a3 = a1_value + a2_value + a3_value
    #     if "a4-a5" in columns:
    #         self.gwp_a4_a5 = self.convert_to_float(gwp_df["a4-a5"].values[0].replace(" ", ""))
    #     else:
    #         a4_value = self.convert_to_float(gwp_df["a4"].values[0].replace(" ", "")) if "a4" in gwp_df.columns else 0.0
    #         a5_value = self.convert_to_float(gwp_df["a5"].values[0].replace(" ", "")) if "a5" in gwp_df.columns else 0.0
    #         self.gwp_a4_a5 = a4_value + a5_value
    #     if "b1-b7" in columns:
    #         self.gwp_b1_b7 = self.convert_to_float(gwp_df["b1-b7"].values[0].replace(" ", ""))
    #     else:
    #         b1_value = self.convert_to_float(gwp_df["b1"].values[0].replace(" ", "")) if "b1" in gwp_df.columns else 0.0
    #         b2_value = self.convert_to_float(gwp_df["b2"].values[0].replace(" ", "")) if "b2" in gwp_df.columns else 0.0
    #         b3_value = self.convert_to_float(gwp_df["b3"].values[0].replace(" ", "")) if "b3" in gwp_df.columns else 0.0
    #         b4_value = self.convert_to_float(gwp_df["b4"].values[0].replace(" ", "")) if "b4" in gwp_df.columns else 0.0
    #         b5_value = self.convert_to_float(gwp_df["b5"].values[0].replace(" ", "")) if "b5" in gwp_df.columns else 0.0
    #         b6_value = self.convert_to_float(gwp_df["b6"].values[0].replace(" ", "")) if "b6" in gwp_df.columns else 0.0
    #         b7_value = self.convert_to_float(gwp_df["b7"].values[0].replace(" ", "")) if "b7" in gwp_df.columns else 0.0
    #         self.gwp_b1_b7 = b1_value + b2_value + b3_value + b4_value + b5_value + b6_value + b7_value
    #     if "c1-c4" in columns:
    #         self.gwp_c1_c4 = self.convert_to_float(gwp_df["c1-c4"].values[0].replace(" ", ""))
    #     else:
    #         c1_value = self.convert_to_float(gwp_df["c1"].values[0].replace(" ", "")) if "c1" in gwp_df.columns else 0.0
    #         c2_value = self.convert_to_float(gwp_df["c2"].values[0].replace(" ", "")) if "c2" in gwp_df.columns else 0.0
    #         c3_value = self.convert_to_float(gwp_df["c3"].values[0].replace(" ", "")) if "c3" in gwp_df.columns else 0.0
    #         c4_value = self.convert_to_float(gwp_df["c4"].values[0].replace(" ", "")) if "c4" in gwp_df.columns else 0.0
    #         self.gwp_c1_c4 = c1_value + c2_value + c3_value + c4_value
    #     if "d" in columns:
    #         self.gwp_d = self.convert_to_float(gwp_df["d"].values[0].replace(" ", ""))
    #     else:
    #         self.gwp_d = 0.0

    def extract_property(self):
        if self.check_property_components():
            self.factor_properties_df = self.df
            self.extract_property_name_value_unit_by_ai()
            return self.extract_property_name_value_unit_by_ai()

    def check_property_components(self):
        contains_property_components = self.df.apply(lambda row:
                                                     RowOperator.check_indicator(row, 'product-components',
                                                                                 True),
                                                     axis=1).any()
        contains_property_component = self.df.apply(lambda row:
                                                    RowOperator.check_indicator(row, 'product-component',
                                                                                True),
                                                    axis=1).any()

        return contains_property_components or contains_property_component

    def extract_property_name_value_unit_by_ai(self):
        ai_extractor = AiExtractor(self.factor_properties_df)
        requirement = ("Extract the property in the dataframe, put them in a list, the name of it should be accurate,"
                       "For example:"
                       "Property list: [(Cement_Weight, 200, kg), (PPS_Height, 30, cm), (Wide, 20, m)], "
                       "only give me the result list, no other things")
        result = ai_extractor.csv_requirement(requirement)
        result = self.__ai_feed_back_extractor(result)
        result = self.modify_totals(result)
        self.property_list_2 = result
        return result

    @staticmethod
    def __ai_feed_back_extractor(text):
        # Define the regex pattern to match each property tuple
        pattern = r"\('([^']+)', ([\d\.]+), '([^']+)'\)"
        matches = re.findall(pattern, text)

        # Convert the matched strings to the required tuple format
        property_list = [(match[0], float(match[1]), match[2]) for match in matches]

        return property_list

    @staticmethod
    def modify_totals(data):
        modified_data = []
        total_found = False

        for item in data:
            label, value, unit = item

            if label.lower() == 'total':
                if not total_found:
                    modified_data.append(('Weight', value, unit))
                    total_found = True
            else:
                modified_data.append(item)

        return modified_data

    @staticmethod
    def __extract_property_unit(column_name):
        pattern = r'\(([^)]+)\)|,\s*(\w+)'
        match = re.search(pattern, column_name)
        if match:
            return match.group(1) if match.group(1) else match.group(2)
        return ''

    # @staticmethod
    # def __extract_property_unit(column_name):

    def __extract_product_components(self):
        """
        Extracts product components and their weights from the given CSV file.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            list: A list of strings in the format "Component: Weight".
        """
        # Load the CSV file
        df = self.df

        # Convert column names to lowercase to ensure case-insensitive matching
        df.columns = df.columns.str.lower()

        # Find the index of the row containing 'total'
        if len(df[df.iloc[:, 0].str.lower() == 'total']) > 0:
            total_index = df[df.iloc[:, 0].str.lower() == 'total'].index[0]
            df.iloc[total_index, 0] = 'Weight'

            # Extract rows from 'product components' to 'total'
            extracted_df = df.iloc[:total_index + 1, [0, 1]]

            # Create the list of "Component: Weight" strings
            components_list = [f"{row[0]}: {row[1]}" for row in extracted_df.itertuples(index=False)]
            return components_list
        else:
            return []

    def get_df(self):
        return self.df

    def get_factor_properties_df(self):
        return self.factor_properties_df

    def get_property_unit(self):
        return self.property_unit

    def get_property_list(self):
        return self.property_list

    def get_gwp_a1_a3(self):
        return self.gwp_a1_a3

    def get_gwp_a4_a5(self):
        return self.gwp_a4_a5

    def get_gwp_b1_b7(self):
        return self.gwp_b1_b7

    def get_gwp_c1_c4(self):
        return self.gwp_c1_c4

    def get_gwp_d(self):
        return self.gwp_d


if __name__ == "__main__":
    csv_path = '/Users/apple/PycharmProjects/pdf_server_2.1/core/server/inference_results/www.environdec.com:library:epd1346/csv'
    table_extractor = TableExtractor()
    table_extractor.multiple_csvs_extracts(csv_path)
    table_extractor.show_value()

    # 4546 8559
