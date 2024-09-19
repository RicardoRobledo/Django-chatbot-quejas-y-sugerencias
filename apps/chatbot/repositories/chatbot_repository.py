from django.conf import settings

import tiktoken

from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from apps.base.utils.managers import GoogleSheetManager, PromptManager


async def send_message(thread_id: str, message: str):

    # Making prompt
    prompt = await PromptManager.read_prompt('prompt_message')
    prompt_result = PromptManager.fill_out_prompt(prompt, {'message': message})

    # Sending prompt message
    await OpenAISingleton.create_message(thread_id, prompt_result)
    run = await OpenAISingleton.run_thread(thread_id)

    # Getting answer
    response = await OpenAISingleton.retrieve_message(run, thread_id)

    return response


async def send_date_range(thread_id: str, dates: dict):
    """
    This function sends a message to the chatbot with the date range

    :param thread_id: thread id
    :param dates: dictionary with date range
    :return: number of tokens in the table
    """

    # Getting table from google sheets in json format
    json_table = await GoogleSheetManager.convert_table_from_dates(dates)

    # Making prompt
    prompt = await PromptManager.read_prompt('prompt_table')
    prompt_result = PromptManager.fill_out_prompt(
        prompt, {'json_table': json_table})

    # Counting tokens
    encoding = tiktoken.encoding_for_model(settings.ASSISTANT_MODEL)

    tokens = encoding.encode(json_table)
    num_tokens = len(tokens)

    print(f'Number of tokens: {num_tokens}')

    # Sending prompt message
    await OpenAISingleton.create_message(thread_id, prompt_result)

    return num_tokens if num_tokens != 1 else 0
