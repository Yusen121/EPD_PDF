import requests


class DeeplTranslate:
    def __init__(self, api_key):
        self.api_key = api_key

    def translate_ch(self, eg_word: str) -> str:
        text = eg_word
        # Source and target languages
        source_lang = 'EN'
        target_lang = 'ZH'

        # API endpoint
        url = 'https://api-free.deepl.com/v2/translate'

        # Request parameters
        params = {
            'auth_key': self.api_key,
            'text': text,
            'source_lang': source_lang,
            'target_lang': target_lang
        }

        # Make the request
        response = requests.post(url, data=params)
        # Check for a successful response
        if response.status_code == 200:
            result = response.json()
            translated_text = result['translations'][0]['text']
            return translated_text
        else:
            raise Exception(f'Error: {response.status_code} - {response.text}')
