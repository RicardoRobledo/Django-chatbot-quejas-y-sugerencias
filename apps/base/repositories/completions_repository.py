from datetime import datetime

from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from apps.base.utils.managers import GoogleSheetManager, PromptManager


async def full_completion():

    # Getting full table
    json_table = await GoogleSheetManager.convert_full_table()

    # Making prompts
    complaints_prompt = await PromptManager.read_prompt('prompt_admin_complaints')
    suggestions_prompt = await PromptManager.read_prompt('prompt_admin_suggestions')

    complaints_result = PromptManager.fill_out_prompt(
        complaints_prompt, {'json_table': json_table})
    suggestions_result = PromptManager.fill_out_prompt(
        suggestions_prompt, {'json_table': json_table})

    response = await OpenAISingleton.create_full_completion_admin(complaints_result, suggestions_result)

    return response


async def completion_by_month(month: str):

    # Obtener el año actual
    current_year = datetime.now().year

    json_table = await GoogleSheetManager.get_complaints_suggestions_by_month_and_year(month, current_year)

    # Making prompts
    complaints_prompt = await PromptManager.read_prompt('prompt_admin_complaints')
    suggestions_prompt = await PromptManager.read_prompt('prompt_admin_suggestions')

    complaints_result = PromptManager.fill_out_prompt(
        complaints_prompt, {'json_table': json_table})
    suggestions_result = PromptManager.fill_out_prompt(
        suggestions_prompt, {'json_table': json_table})

    response = await OpenAISingleton.create_month_completion_admin(complaints_result, suggestions_result)

    return response
