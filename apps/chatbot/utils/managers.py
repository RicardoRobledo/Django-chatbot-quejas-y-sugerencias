from string import Template

import pandas as pd

from django.conf import settings


__author__ = 'Ricardo Robledo'
__version__ = '1.0'


class GoogleSheetManager():


    @classmethod
    async def read_google_sheets(cls):
        """
        This method read the google sheet and return the a string representation of the data.
        """

        df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{settings.GOOGLE_SHEET_ID}/export?format=csv')
        df = df.drop(columns=['Correo', 'Nombre'])
        df['Fecha del mensaje'] = pd.to_datetime(df['Fecha del mensaje'], format='%d/%m/%Y %H:%M:%S')

        return df


def read_prompt(prompt_file:str):
    """
    This method read a file and return a prompt template
    """

    with open(f'apps/chatbot/prompts/{prompt_file}.txt') as file:
        file_content = file.read()

    return file_content


def fill_out_prompt(prompt:str, variables:dict):
    """
    This method fill out a prompt template

    :return: prompt filled out
    """

    prompt_result = Template(prompt).substitute(**variables)

    return prompt_result
