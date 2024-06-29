from string import Template
from datetime import datetime

import pandas as pd
from tabulate import tabulate

from django.conf import settings


__author__ = 'Ricardo Robledo'
__version__ = '1.0'


def normalize_date(date:str):

    date_string = date.replace('Z', '+00:00')
    date = datetime.fromisoformat(date_string)
    normalized_date = date.strftime('%Y-%m-%d')

    return normalized_date


class GoogleSheetManager():


    @classmethod
    async def read_google_sheets(cls):
        """
        This method read the google sheet and return the a string representation of the data.
        """

        df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{settings.GOOGLE_SHEET_ID}/export?format=csv')
        df['Fecha del mensaje'] = pd.to_datetime(df['Fecha del mensaje'], format='%d/%m/%Y %H:%M:%S')

        return df


    @classmethod
    async def convert_table_from_dates(cls, dates:dict):
        """
        This method build a markdown table from a pandas dataframe given a date range.

        :param dates: dictionary with date range
        :return: markdown table
        """

        result = await cls.read_google_sheets()
        result['Fecha del mensaje'] = result['Fecha del mensaje'].dt.normalize()

        from_date = normalize_date(dates['from_date'])
        to_date = normalize_date(dates['to_date'])

        filtered_result = result[
            (result['Fecha del mensaje'] >= from_date) &
            (result['Fecha del mensaje'] <= to_date)
        ]

        return tabulate(filtered_result, headers='keys', tablefmt='pipe', showindex=False)


class PromptManager():


    @classmethod
    def read_prompt(cls, prompt_file:str):
        """
        This method read a file and return a prompt template

        :param prompt_file: file name to make the prompt
        """

        with open(f'apps/chatbot/prompts/{prompt_file}.txt') as file:
            file_content = file.read()

        return file_content


    @classmethod
    def fill_out_prompt(cls, prompt:str, variables:dict):
        """
        This method fill out a prompt template

        :return: prompt filled out
        """

        return Template(prompt).substitute(**variables)
