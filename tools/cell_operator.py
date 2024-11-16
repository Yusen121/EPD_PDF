import re

import pandas as pd


class CellOperator:
    @staticmethod
    def lowercase_no_symbol(text):
        if isinstance(text, str) and pd.notna(text):
            return re.sub(r'\W+', '', text).lower()
        return text

    @staticmethod
    def lowercase_has_symbol(text):
        if isinstance(text, str) and pd.notna(text):
            return text.lower()
        return text
