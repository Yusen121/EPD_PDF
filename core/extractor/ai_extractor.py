import os
import pandas as pd
from time import sleep
from config import Default
from core.extractor.info_extractor import InfoExtractor
from langchain.chains import LLMChain
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate


class AiExtractor(InfoExtractor):
    default = Default()

    def __init__(self, df=None, txt=None):
        super().__init__()
        self.api_key = self.default.api_key
        os.environ["DASHSCOPE_API_KEY"] = self.api_key
        self.df = df
        self.read_text = txt

    def load_csv(self, csv_path):
        self.df = pd.read_csv(csv_path)
        return self.df

    def text_requirement(self, requirement):
        prompt_template = f"""{requirement}, given this text {{text}}"""

        text_preview = self.read_text
        prompt = PromptTemplate(template=prompt_template, input_variable=["text"])
        llm = Tongyi(api_key=self.api_key)
        chain = LLMChain(llm=llm, prompt=prompt)
        while True:
            try:
                response = chain.run(text=text_preview)
                break
            except Exception as e:
                if "rate limit" in str(e).lower():
                    print("Rate limit exceeded. Retrying in 60 seconds...")
                    sleep(60)
                else:
                    raise e
        return response

    def csv_requirement(self, requirement):
        prompt_template = f"""{requirement}, given this dataframe {{dataframe}}"""
        dataframe_preview = self.df.to_string()
        prompt = PromptTemplate(template=prompt_template, input_variable=["dataframe"])
        llm = Tongyi(api_key=self.api_key)
        chain = LLMChain(llm=llm, prompt=prompt)
        while True:
            try:
                response = chain.run(dataframe=dataframe_preview)
                break
            except Exception as e:
                if "rate limit" in str(e).lower():
                    print("Rate limit exceeded. Retrying in 60 seconds...")
                    sleep(60)
                else:
                    raise e
        return response


if __name__ == "__main__":
    csv_extractor = AiExtractor()
    csv_path = '/Users/apple/PycharmProjects/EPDLibrary/data/try_output_1/pdf/f54eaec8-d921-4aec-8af3-bf89313b68a9/split_method/table_page_6_table_1.csv'
    csv_extractor.load_csv(csv_path)
    print(csv_extractor.csv_requirement("I want you to get the property's name, value, and property, then"
                                        "put them in a list, only give me the result"))

