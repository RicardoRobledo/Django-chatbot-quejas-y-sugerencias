import io

from string import Template
from datetime import datetime

import pandas as pd
import tiktoken
import matplotlib.pyplot as plt
import base64

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

    @classmethod
    async def convert_full_table(cls):
        """
        This method convert the full table to a json string
        """

        result = await cls.read_google_sheets()

        result['Fecha del mensaje'] = result['Fecha del mensaje'].astype(str)

        json_data = result.to_json(
            orient='records', lines=True, force_ascii=False)

        # Limiting the number of tokens
        adjusted_text = TokenManager.fit_token_limit(
            json_data[-settings.TOKEN_LIMIT:])

        return adjusted_text

    @classmethod
    async def get_number_complaints_suggestions_by_month(cls):

        # Read the google sheet
        result = await cls.read_google_sheets()

        # Convert 'Fecha del mensaje' to datetime
        result['Fecha del mensaje'] = pd.to_datetime(
            result['Fecha del mensaje'])

        # Get the current year
        current_year = datetime.now().year

        # Filtrar filas por el año actual
        result_current_year = result[result['Fecha del mensaje'].dt.year == current_year].copy(
        )

        # Crear una nueva columna para el número del mes (evitar advertencia con .loc)
        result_current_year.loc[:, 'Numero de quejas por mes'] = result_current_year['Fecha del mensaje'].dt.month.astype(
            int)

        # Agrupar por el número del mes y contar el número de quejas/sugerencias por mes
        complaints_by_month = result_current_year.groupby(
            'Numero de quejas por mes').size()

        # Crear un diccionario con el nombre del mes en español
        month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
            7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        # Convertir el resultado a un diccionario con los nombres de los meses
        complaints_by_month_dict = [
            {
                'month': month_names[month],
                'number_complaints_suggestions': int(complaints_by_month.get(month, 0))
            } for month in range(1, 13)
        ]

        return complaints_by_month_dict

    @classmethod
    async def get_complaints_suggestions_by_month_and_year(cls, month: int, year: int):
        """
        This method filters the complaints and suggestions based on a given month and year.

        :param month: The month to filter (1-12)
        :param year: The year to filter
        :return: A list of complaints for the specified month and year
        """

        result = await cls.read_google_sheets()

        # Convertir 'Fecha del mensaje' a datetime
        result['Fecha del mensaje'] = pd.to_datetime(
            result['Fecha del mensaje'])

        # Obtener el año actual
        current_year = datetime.now().year

        # Filtrar por el año actual
        result_current_year = result[result['Fecha del mensaje'].dt.year == current_year]

        # Filtrar por el mes solicitado
        filtered_result = result_current_year[result_current_year['Fecha del mensaje'].dt.month == month]

        json_data = filtered_result.to_json(
            orient='records', lines=True, force_ascii=False)

        # Limiting the number of tokens
        adjusted_text = TokenManager.fit_token_limit(
            json_data[-settings.TOKEN_LIMIT:])

        return adjusted_text


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


class GraphManager():

    @classmethod
    def create_graph(cls, title: str, attributes: list, labels: list):
        """
        This method creates a graph (bar chart) from a list of data.

        Parameters:
        - title (str): The title of the graph.
        - attributes (list): A list of category names or attributes (e.g., the names of categories).
        - labels (list): A list of values corresponding to each attribute (e.g., counts or numbers).

        Returns:
        - str: A base64-encoded string of the generated graph image in PNG format.

        This method uses a dark theme and assigns a unique color to each bar in the chart.
        The chart is created in memory and converted to a base64-encoded PNG image, 
        which can be used in web responses or for embedding directly into HTML.
        """

        # List of different colors for each bar
        colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        # Create the bar chart in memory with a dark background
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(attributes, labels, color=colores)

        # Add labels and title
        ax.set_xlabel('Sentencia', color='white',
                      fontsize=12)  # Reduce font size
        ax.set_ylabel('Cantidad', color='white', fontsize=12)
        ax.set_title(title, color='white', fontsize=14)
        ax.tick_params(colors='white', which='both')

        # Rotate the labels on the x-axis to avoid overlap
        # Reduce font size of x-axis labels
        plt.xticks(rotation=45, ha='right', fontsize=10)

        # Adjust the margins manually to prevent label cutoff
        # Adjust bottom/top margin to fit the labels and title
        plt.subplots_adjust(bottom=0.35, top=0.85)

        # Save the graph to a BytesIO object in PNG format
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        # Convert the image in the buffer to base64
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Close the buffer to release memory
        buf.close()

        # Return the base64-encoded image
        return image_base64
