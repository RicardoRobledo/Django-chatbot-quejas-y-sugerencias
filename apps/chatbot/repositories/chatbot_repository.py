from ...desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from ..utils.managers import GoogleSheetManager, PromptManager
 

async def send_message(thread_id:str, message:str):

    # Making prompt
    prompt = await PromptManager.read_prompt('prompt_message')
    prompt_result = PromptManager.fill_out_prompt(prompt, {'message':message})

    # Sending prompt message
    await OpenAISingleton.create_message(thread_id, prompt_result)
    run = await OpenAISingleton.run_thread(thread_id)

    # Getting answer
    return await OpenAISingleton.retrieve_message(run, thread_id)


async def send_date_range(thread_id:str, dates:dict):

    # Getting table from google sheets in markdown format
    markdown_table = await GoogleSheetManager.convert_table_from_dates(dates)

    # Making prompt
    prompt = await PromptManager.read_prompt('prompt_table')
    prompt_result = PromptManager.fill_out_prompt(prompt, {'markdown_table':markdown_table})

    print(prompt)
    print('-------------------')
    print(prompt_result)
    print('-------------------')
    print(markdown_table)

    # Sending prompt message
    await OpenAISingleton.create_message(thread_id, prompt_result)
