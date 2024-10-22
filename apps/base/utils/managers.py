from string import Template

import tiktoken


from django.conf import settings


__author__ = 'Ricardo Robledo'
__version__ = '1.0'


class PromptManager():

    @ classmethod
    async def read_prompt(cls, prompt_file: str):
        """
        This method read a file and return a prompt template

        :param prompt_file: file name to make the prompt
        """

        import aiofiles

        async with aiofiles.open(f'apps/base/prompts/{prompt_file}.txt', mode='r', encoding='utf-8') as file:
            file_content = await file.read()

        return file_content

    @ classmethod
    def fill_out_prompt(cls, prompt: str, variables: dict):
        """
        This method fill out a prompt template

        :return: prompt filled out
        """

        return Template(prompt).substitute(**variables)


class TokenManager():

    __encoding = tiktoken.encoding_for_model("gpt-4")

    @classmethod
    def fit_token_limit(cls, text: str):

        if len(cls.__encoding.encode(text)) > settings.TOKEN_LIMIT:

            tokens = tokens[-settings.TOKEN_LIMIT:]
            adjusted_text = cls.__encoding.decode(tokens)

            return adjusted_text

        else:
            return text
