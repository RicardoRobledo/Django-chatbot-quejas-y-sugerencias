from string import Template
from datetime import datetime

import pandas as pd

from django.conf import settings


__author__ = 'Ricardo Robledo'
__version__ = '1.0'


def normalize_date(date: str):

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

        df = pd.read_csv(
            f'https://docs.google.com/spreadsheets/d/{settings.GOOGLE_SHEET_ID}/export?format=csv')
        df['Fecha del mensaje'] = pd.to_datetime(
            df['Fecha del mensaje'], format='%d/%m/%Y %H:%M:%S').dt.date

        return df

    @classmethod
    async def convert_table_from_dates(cls, dates: dict):
        """
        This method build a markdown table from a pandas dataframe given a date range.

        :param dates: dictionary with date range
        :return: markdown table
        """

        result = await cls.read_google_sheets()

        from_date = pd.to_datetime(dates['from_date']).date()
        to_date = pd.to_datetime(dates['to_date']).date()

        filtered_result = result[
            (result['Fecha del mensaje'] >= from_date) &
            (result['Fecha del mensaje'] <= to_date)
        ].copy()

        print(f'Number of filtered rows: {filtered_result.shape[0]}')

        # No empezar diciendo que se genere una grafica directamente, sino posteriormente de que se haya preguntado algo
        filtered_result['Fecha del mensaje'] = filtered_result['Fecha del mensaje'].astype(
            str)

        json_data = filtered_result.to_json(
            orient='records', lines=True, force_ascii=False)

        return json_data


class PromptManager():

    @classmethod
    async def read_prompt(cls, prompt_file: str):
        """
        This method read a file and return a prompt template

        :param prompt_file: file name to make the prompt
        """

        import aiofiles

        async with aiofiles.open(f'apps/chatbot/prompts/{prompt_file}.txt') as file:
            file_content = await file.read()

        return file_content

    @classmethod
    def fill_out_prompt(cls, prompt: str, variables: dict):
        """
        This method fill out a prompt template

        :return: prompt filled out
        """

        return Template(prompt).substitute(**variables)
