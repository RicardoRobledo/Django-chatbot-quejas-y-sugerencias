import time
import base64
import asyncio

from django.conf import settings
from http import HTTPStatus
from openai import AsyncOpenAI
# from openai.types.beta.threads import ImageFileContentBlock, TextContentBlock
from apps.base.schemas.openai_schemas import Complaints, Suggestions
from apps.base.utils.managers import GraphManager, GoogleSheetManager


__author__ = 'Ricardo'
__version__ = '1.0'


class OpenAISingleton():

    __client = None

    @classmethod
    def __get_connection(self):
        """
        This method create our client and give us a new thread
        """

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,)

        return client

    def __new__(cls, *args, **kwargs):

        if cls.__client == None:

            # making connection
            cls.__client = cls.__get_connection()

        return cls.__client

    @classmethod
    async def create_thread(cls):
        """
        This method create a new thread

        :return: thread_id
        """
        return await cls.__client.beta.threads.create()

    @classmethod
    async def delete_thread(cls, thread_id: str):
        """
        This method delete a thread

        :param:
        """
        return await cls.__client.beta.threads.delete(thread_id)

    @classmethod
    async def create_completion_message(cls, user_message: str):
        """
        This method create a new completion message to single tasks

        :param message: a string being our message
        :return: a completion message
        """

        message = {'data': {}, 'status_code': HTTPStatus.OK}

        response = await cls.__client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system",
                    "content": "Eres un asistente de AI experto en detectar intenciones de usuarios, debes de verificar si el siguiente mensaje tiene la intención de crar una gráfica, debes responder (Sí/No)"},
                {"role": "user",
                    "content": user_message},
            ]
        )

        response_message = response.choices[0].message.content

        return response_message

    @classmethod
    async def create_year_completion_admin(cls, prompt_complaints: str, prompt_suggestions: str, year: int):
        """
        This method create a new completion message taking full data

        :param prompt_complaints: a string being our prompt for complaints
        :param prompt_suggestions: a string being our prompt for suggestions
        :param year: an integer being our year
        :return: a completion message
        """

        message = {'data': {}, 'status_code': HTTPStatus.OK}

        system_message = "Eres un asistente de ia avanzada que ayuda en un departamento de recursos humanos clasificando quejas y sugerencias y dando porcentajes sobre que tan importantes son cierto tipo de quejas"

        completion_complaints = cls.__client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_complaints},
            ],
            response_format=Complaints,
        )

        completion_suggestions = cls.__client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_suggestions},
            ],
            response_format=Suggestions,
        )

        completion_complaints, completion_suggestions = await asyncio.gather(
            completion_complaints, completion_suggestions
        )

        # Getting complaints data
        complaints_response = completion_complaints.choices[0].message.parsed
        complaints = complaints_response.complaints
        complaints_percentages = complaints_response.percentages

        # Getting suggestions data
        suggestions_response = completion_suggestions.choices[0].message.parsed
        suggestions = suggestions_response.suggestions
        suggestions_percentages = suggestions_response.percentages

        # Getting number of complaints and suggestions by month
        number_complaints_suggestions_by_month = await GoogleSheetManager.get_number_complaints_suggestions_by_month(year)

        # Making graphs
        complaints_graph = GraphManager.create_graph('Quejas',
                                                     complaints, complaints_percentages)
        suggestion_graph = GraphManager.create_graph('Sugerencias',
                                                     suggestions, suggestions_percentages)

        message['data'] = {'number_complaints_suggestions_by_month': number_complaints_suggestions_by_month,
                           'complaints_response': {'complaints': complaints, 'percentages': complaints_percentages, 'graph': complaints_graph},
                           'suggestions_response': {'suggestions': suggestions, 'percentages': suggestions_percentages, 'graph': suggestion_graph}}

        return message

    @classmethod
    async def create_month_completion_admin(cls, prompt_complaints: str, prompt_suggestions: str):
        """
        This method create a new completion message taking full data

        :param prompt_complaints: a string being our prompt for complaints
        :param prompt_suggestions: a string being our prompt for suggestions
        :return: a completion message
        """

        message = {'data': {}, 'status_code': HTTPStatus.OK}

        system_message = "Eres un asistente de ia avanzada que ayuda en un departamento de recursos humanos clasificando quejas y sugerencias y dando porcentajes sobre que tan importantes son cierto tipo de quejas"

        completion_complaints = cls.__client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_complaints},
            ],
            response_format=Complaints,
        )

        completion_suggestions = cls.__client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_suggestions},
            ],
            response_format=Suggestions,
        )

        completion_complaints, completion_suggestions = await asyncio.gather(
            completion_complaints, completion_suggestions
        )

        # Getting complaints data
        complaints_response = completion_complaints.choices[0].message.parsed
        complaints = complaints_response.complaints
        complaints_percentages = complaints_response.percentages

        # Getting suggestions data
        suggestions_response = completion_suggestions.choices[0].message.parsed
        suggestions = suggestions_response.suggestions
        suggestions_percentages = suggestions_response.percentages

        # Making graphs
        complaints_graph = GraphManager.create_graph('Quejas',
                                                     complaints, complaints_percentages)
        suggestion_graph = GraphManager.create_graph('Sugerencias',
                                                     suggestions, suggestions_percentages)

        message['data'] = {'complaints_response': {'complaints': complaints, 'percentages': complaints_percentages, 'graph': complaints_graph},
                           'suggestions_response': {'suggestions': suggestions, 'percentages': suggestions_percentages, 'graph': suggestion_graph}}

        return message

    @classmethod
    async def create_message(cls, thread_id: str, message: str):
        """
        This method create a new message in the assistant
        """

        message = await cls.__client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        return message

    @classmethod
    async def run_thread(cls, thread_id: str):
        """
        This method run our thread to process a response the answer from the assistant
        """

        run = await cls.__client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=settings.ASSISTANT_ID
        )

        i = 0
        while run.status == "queued" or run.status == "in_progress":

            run = await cls.__client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )

            print(f'{run.status} - {i}')
            i += 1

            time.sleep(0.1)

            # if run.status=='failed':
            #    print(run.last_error)
            #    print(run.last_error.code)

        print(run)

        return run

    @classmethod
    async def retrieve_message(cls, run, thread_id: str):
        """
        This method return the answer from the assistant
        """

        message = {'data': {}, 'status_code': HTTPStatus.OK}

        if run.status == 'failed' and run.last_error.code == 'rate_limit_exceeded':

            message['data'] = {
                'msg': 'Error, el límite de cuota ha sido alcanzado, por favor verifique su crédito', 'error': 'rate_limit_exceeded'}
            message['status_code'] = HTTPStatus.PAYMENT_REQUIRED

            return message

        messages = (await cls.__client.beta.threads.messages.list(
            thread_id=thread_id
        )).data[0].content

        if len(messages) == 1:
            message['data'] = {'msg': messages[0].text.value}
        else:

            image = messages[0]

            image_file_id = image.image_file.file_id
            image_file = await cls.__client.files.content(image_file_id)

            # ImageFileContentBlock - TextContentBlock
            message['data'] = {'img': base64.b64encode(image_file.read()).decode(
                'utf-8'), 'msg': messages[1].text.value}

        return message

    @classmethod
    async def create_conversation_thread(cls):
        """
        Make up a thread conversation
        """

        return await cls.__client.beta.threads.create()

    @classmethod
    async def delete_conversation_thread(cls, thread_id):
        """
        Remove a thread converation

        :param thread: an string being our thread identifier
        """

        cls.__client.beta.threads.delete(thread_id)
