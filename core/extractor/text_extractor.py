import re
from config import Default
from core.extractor.ai_extractor import AiExtractor
from core.extractor.info_extractor import InfoExtractor
from log.log import logger
# Todo, 用大模型分片打上标签 meta data

class TextExtractor(InfoExtractor):
    default = Default()

    def __init__(self):
        super().__init__()
        self.aiextractor = None

    def multiple_text_extract(self, texts: list):
        for text in texts:
            try:
                self.txt_extract(text)
            except Exception as e:
                logger.error(f'The error is {e}, {text}')
                raise

    def txt_extract(self, text):
        self.text = text
        self.aiextractor = AiExtractor(txt=self.text)
        # LCA Information
        if self.__is_LCA_info(text):
            self.__extract_unit()

        # Product Information/ Description
        if self.__is_product_info(text):
            self.extract_name()
            self.__extract_location()
            self.__extract_description()
            if not self.unit:
                self.__extract_unit()
        # environment_product_declaration
        if self.__is_environment_product_declaration(text):
            self.__extract_sample_start_time()
            self.__extract_sample_end_time()
            self.__extract_valid_time()
            if not self.name_en:
                self.extract_name()


    def extract_name(self):
        name_string = self.aiextractor.text_requirement(
            "Get the product name of product as complete as possible by using this format: Product Name: Cement(G86), "
            "Cement is an example"
            "if there is two product, separate it by comma, like Product Name: Cement(G86), Cement(G33)"
            "if there has a Product number，put it inside brackets")
        # print(name_string)
        self.name_en = self.result_name(name_string)
        # name_en_match = re.search(r'Product name:\s*(.*?)\s*Product identification', self.text, re.IGNORECASE)
        # if name_en_match:
        #     self.name_en = name_en_match.group(1).strip()

    @staticmethod
    def result_name(name):
        match = re.search(r'Product Name:\s*(.*)', name, re.IGNORECASE)
        # match = re.search(r'Product Name: ([\w\s]+)', name)
        # match = re.search(r'Product Name:\s*([\w\s\(\)/]+)', name)
        if match:
            match_name = match.group(1).strip()
            result_name = re.sub(r'[^\w\s\(\)/,]', '', match_name)
            # result_name = re.sub(r'[^\w\s]', '', match_name)
            return result_name
        else:
            raise FileNotFoundError('No find Product name')

    def __is_product_info(self, s: str) -> bool:
        decision_1 = 'product information' in s.lower()
        decision_2 = 'product description' in s.lower()
        total_decision = decision_1 or decision_2
        return total_decision

    def __is_LCA_info(self, s: str) -> bool:
        return 'lca information' in s.lower()

    def __is_environment_product_declaration(self, s: str) -> bool:
        normalized_string = s.lower().replace(' ', '').replace('\n', '')
        search_phrase = 'environmentalproductdeclaration'
        return search_phrase in normalized_string

    def __extract_product_identification(self):
        identification_match = re.search(r'Product identification:\s*(.*?)\s*Product description',
                                         self.text, re.IGNORECASE)
        if identification_match:
            self.identification = identification_match.group(1).strip()

    def __extract_unit(self):
        # Todo: 用json形式， 重试机制3-5, 重试装饰器
        declared_unit_string = self.aiextractor.text_requirement(
            "Get the product declared unit, give me only the declared unit using this format: Declared Unit: kg, "
            "remember, only the mathematical unit, not other description"
            "kg is an example")
        self.unit = self.result_unit(declared_unit_string)

    @staticmethod
    def result_unit(unit):
        match = re.search(r'Declared Unit: ([\w\s]+)', unit)
        if match:
            match_unit = match.group(1).strip()
            result_unit = re.sub(r'[^\w\s]', '', match_unit)
            return result_unit
        # else:
        #     raise FileNotFoundError('No found declare unit')
    # Todo: decide whether to replace Valid unit by \n

    def __extract_sample_start_time(self):
        sample_start_match_1 = re.search(r'Publication date:\s*(.*?)\s*Valid until', self.text, re.IGNORECASE)
        sample_start_match_2 = re.search(r'Published:\s*(.*?)\s*\n', self.text, re.IGNORECASE)
        if sample_start_match_1:
            self.sample_start = sample_start_match_1.group(1).strip()
        elif sample_start_match_2:
            self.sample_start = sample_start_match_2.group(1).strip()

    def __extract_sample_end_time(self):
        sample_end_time_1 = re.search(r'Publication date:\s*(.*?)\s*Valid until', self.text, re.IGNORECASE)
        sample_end_time_2 = re.search(r'Published:\s*(.*?)\s*\n', self.text, re.IGNORECASE)
        if sample_end_time_1:
            self.sample_end = sample_end_time_1.group(1).strip()
        elif sample_end_time_2:
            self.sample_end = sample_end_time_2.group(1).strip()

    def __extract_valid_time(self):
        phase = 'An EPD should provide current information and may be updated if conditions change.'
        pattern = rf'Valid until:\s*(.*?)\s*{re.escape(phase)}'
        valid_time_match_1 = re.search(pattern, self.text, re.IGNORECASE)
        valid_time_match_2 = re.search(r'Valid until:\s*(.*?)\s*\n', self.text, re.IGNORECASE)
        if valid_time_match_1:
            self.valid_time = valid_time_match_1.group(1).strip()
        elif valid_time_match_2:
            self.valid_time = valid_time_match_2.group(1).strip()

    def __extract_location(self):
        location_string = self.aiextractor.text_requirement(
            "Get the Geographical scope of product, give me only the Geographical scope using this format: Product "
            "Location: US,"
            "US is an example"
            "if there is no geographical scope, return Product Location: None")
        self.location = self.__result_location(location_string)

    @staticmethod
    def __result_location(location):
        match = re.search(r'Product Location: ([\w\s]+)', location)
        if match:
            match_location = match.group(1).strip()
            result_location = re.sub(r'[^\w\s]', '', match_location)
            if result_location == 'None':
                return ''
            return result_location
        else:
            raise FileNotFoundError('No location found')

    def __extract_description(self):
        description_string = self.aiextractor.text_requirement(
            "Get the description of product, give me only the description using this format: Description:  "
            "This is an apple,"
            "This is an apple is an example")
        self.description = description_string
