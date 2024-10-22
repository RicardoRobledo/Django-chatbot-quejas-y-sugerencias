from django.conf import settings

import tiktoken
import pandas as pd

from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from apps.base.utils.managers import PromptManager, TokenManager

from apps.custom_admin.models import ComplaintModel, SuggestionModel
from asgiref.sync import sync_to_async


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

    complaints = await sync_to_async(list)(
        ComplaintModel.objects.filter(
            created_at__gte=dates['from_date'],
            created_at__lte=dates['to_date']
        ).values(
            'id', 'description', 'complaint_type__name', 'name', 'email', 'created_at'
        )
    )

    suggestions = await sync_to_async(list)(
        SuggestionModel.objects.filter(
            created_at__gte=dates['from_date'],
            created_at__lte=dates['to_date']
        ).values(
            'id', 'description', 'suggestion_type__name', 'name', 'email', 'created_at'
        )
    )

    df_complaints = pd.DataFrame(complaints)
    df_suggestions = pd.DataFrame(suggestions)

    df_complaints = df_complaints.rename(columns={
        'complaint_type__name': 'Tipo de queja o sugerencia',
        'id': 'ID',
        'description': 'Descripción',
        'name': 'Nombre',
        'email': 'Correo',
        'created_at': 'Fecha de creación'
    })

    df_suggestions = df_suggestions.rename(columns={
        'suggestion_type__name': 'Tipo de queja o sugerencia',
        'id': 'ID',
        'description': 'Descripción',
        'name': 'Nombre',
        'email': 'Correo',
        'created_at': 'Fecha de creación'
    })

    df_combined = pd.concat([df_complaints, df_suggestions], ignore_index=True)
    df_combined['Fecha de creación'] = pd.to_datetime(
        df_combined['Fecha de creación']).dt.date

    json_table = df_combined.to_json(
        orient='records', lines=True, force_ascii=False)

    adjusted_table = TokenManager.fit_token_limit(
        json_table[-settings.TOKEN_LIMIT:])

    # Making prompt
    prompt = await PromptManager.read_prompt('prompt_table')
    prompt_result = PromptManager.fill_out_prompt(
        prompt, {'json_table': adjusted_table})

    # Counting tokens
    encoding = tiktoken.encoding_for_model(settings.OPENAI_MODEL)

    tokens = encoding.encode(adjusted_table)
    num_tokens = len(tokens)

    # Sending prompt message
    await OpenAISingleton.create_message(thread_id, prompt_result)

    return num_tokens if num_tokens != 1 else 0
