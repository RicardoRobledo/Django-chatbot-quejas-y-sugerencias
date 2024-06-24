import time
from openai import AsyncOpenAI

from django.conf import settings


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
        
        if cls.__client==None:

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
    async def delete_thread(cls, thread_id:str):
        """
        This method delete a thread

        :param:
        """
        return await cls.__client.beta.threads.delete(thread_id)


    @classmethod
    async def create_message(cls, thread_id:str, message:str):
        """
        This method create a new message in the assistant
        """

        message = await cls.__client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        return message.id


    @classmethod
    async def run_thread(cls, thread_id:str):
        """
        This method run our thread to process a response the answer from the assistant
        """

        run = await cls.__client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=settings.ASSISTANT_ID
        )

        while run.status == "queued" or run.status == "in_progress":

            run = await cls.__client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )

            time.sleep(0.1)

        return run.id


    @classmethod
    async def retrieve_message(cls, thread_id:str):
        """
        This method return the answer from the assistant
        """

        messages = await cls.__client.beta.threads.messages.list(
            thread_id=thread_id
        )

        return messages.data[0].content[0].text.value


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
