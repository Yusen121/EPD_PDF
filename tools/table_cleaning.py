import pandas as pd


class TableCleaning:
    def __init__(self, table=None):
        self.table = table

    # EFFECTS: return a boolean, if the table is totally empty, which means it has no value in it, return true, or false
    def is_all_null(self):
        return all(all(cell is None or cell == '' for cell in row) for row in self.table)

    # EFFECTS: return a boolean, if the dataframe is empty, return true, if not, return false
    @staticmethod
    def is_dataframe_all_null(df):
        # Replace empty strings with NaN
        df_replaced = df.replace('', float('NaN'))

        # Check if all cells are NaN
        return df_replaced.isna().all().all()

    @staticmethod
    def remove_null_rows_and_columns(df):
        # Replace empty strings with NaN
        df_replaced = df.replace('', float('NaN'))
        # Remove rows where all elements are NaN
        df_cleaned = df_replaced.dropna(how='all')
        # Remove columns where all elements are NaN
        df_cleaned = df_cleaned.dropna(axis=1, how='all')
        return df_cleaned

    @staticmethod
    def is_small_amount_cells(df, threshold=5):
        # # Replace empty strings with NaN
        # df_replaced = df.replace('', float('NaN'))
        #
        # # Count non-NaN cells
        # non_nan_count = df_replaced.notna().sum().sum()
        #
        # # Check if there are one or two cells with values
        # return non_nan_count in [1, 2]
        count = df.size
        return count < threshold

    def rotate_vertical_text(self, df):
        for col in df.columns:
            for idx in df.index:
                cell_value = df.at[idx, col]
                if pd.notna(cell_value) and self.__is_text_vertical(cell_value):
                    df.at[idx, col] = self.__reorient_text(cell_value)
        return df

    @staticmethod
    def __is_text_vertical(text):
        return '\n' in text

    @staticmethod
    def __reorient_text(text):
        lines = text.split('\n')
        reorient_text = ''.join(lines)
        return reorient_text


# if __name__ == "__main__":
#     table_data = [
#         [None, '', 'Value1'],
#         [None, '', None],
#         ['', None, None],
#         [None, None, None]
#     ]
#     table_cleaner = TableCleaning(table_data)
#     print(table_cleaner.table)
#     table_cleaner.remove_null_rows_and_columns()
#     print(table_cleaner.table)
