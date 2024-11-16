from config.default import Default


class ColumnReformat:
    def __init__(self):
        self.coreDefault = Default()

    def factor_info_columns_rearrange(self, df):
        desired_columns = self.coreDefault.factor_info_columns_sequence
        for column in desired_columns:
            if column not in df.columns:
                df[column] = ""
        df = df[desired_columns]
        return df

    def emission_factor_columns_rearrange(self, df):
        desired_columns = self.coreDefault.emission_factor_columns_sequence
        for column in desired_columns:
            if column not in df.columns:
                df[column] = ""
        df = df[desired_columns]
        return df

    def factor_property_columns_rearrange(self, df):
        desired_columns = self.coreDefault.factor_properties_columns_sequence
        for column in desired_columns:
            if column not in df.columns:
                df[column] = ""
        df = df[desired_columns]
        return df

    def property_management_columns_rearrange(self, df):
        desired_columns = self.coreDefault.property_management_columns_sequence
        for column in desired_columns:
            if column not in df.columns:
                df[column] = ""
        df = df[desired_columns]
        return df
