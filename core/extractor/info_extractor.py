class InfoExtractor:
    def __init__(self):
        self.text = None
        self.df = None
        self.name_en = None
        self.identification = None
        self.unit = None
        self.sample_start = None
        self.sample_end = None
        self.valid_time = None
        self.location = None
        self.description = None

    def show_extract_content(self):
        print(self.name_en)
        print(self.unit)
        print(self.sample_start)
        print(self.sample_end)
        print(self.valid_time)
        print(self.location)
        print(self.description)

    def show_value(self):
        print(self.__init__())

    def get_text(self):
        return self.text

    def get_df(self):
        return self.df

    def get_name_en(self):
        return self.name_en

    def get_identification(self):
        return self.identification

    def get_unit(self):
        return self.unit

    def get_sample_start(self):
        return self.sample_start

    def get_sample_end(self):
        return self.sample_end

    def get_valid_time(self):
        return self.valid_time

    def get_location(self):
        return self.location

    def get_description(self):
        return self.description

    def get_property_list(self):
        return self.property_list


