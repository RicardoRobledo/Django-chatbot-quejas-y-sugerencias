from datetime import datetime

from ...desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from ..utils.managers import GoogleSheetManager, read_prompt, fill_out_prompt

from tabulate import tabulate


def normalize_date(date:str):

    date_string = date.replace('Z', '+00:00')
    date = datetime.fromisoformat(date_string)
    normalized_date = date.strftime('%Y-%m-%d')

    return normalized_date
 

async def send_message(dates:str, thread_id:str, message:str):

    result = await GoogleSheetManager.read_google_sheets()
    result['Fecha del mensaje'] = result['Fecha del mensaje'].dt.normalize()

    from_date = normalize_date(dates['from_date'])
    to_date = normalize_date(dates['to_date'])

    filtered_result = result[
        (result['Fecha del mensaje'] >= from_date) &
        (result['Fecha del mensaje'] <= to_date)
    ]
    print(filtered_result)
    markdown_table = tabulate(filtered_result, headers='keys', tablefmt='pipe', showindex=False)

    prompt = read_prompt('prompt_message')
    prompt_result = fill_out_prompt(prompt, {'markdown_table':markdown_table, 'message':message})

    await OpenAISingleton.create_message(thread_id, prompt_result)
    run = await OpenAISingleton.run_thread(thread_id)

    return await OpenAISingleton.retrieve_message(run, thread_id)
