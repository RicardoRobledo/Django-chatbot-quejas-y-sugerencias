from django.conf import settings

import tiktoken

from asgiref.sync import sync_to_async
from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from apps.base.utils.managers import PromptManager

from apps.custom_admin.models import ComplaintTypeModel, SuggestionTypeModel, ComplaintModel, SuggestionModel


async def classify_by_type(complaint_suggestion: str, name: str, email: str):
    """
    This function classify the complaint suggestion by type

    :param complaint_suggestion: The complaint suggestion to classify
    :param name: The name of the user
    :param email: The email of the user
    """

    system_message = "Eres un experto en clasificación de quejas y sugerencias en una empresa de recursos humanos"

    complaint_types = await sync_to_async(list)(ComplaintTypeModel.objects.filter(in_use=True).values_list('name', flat=True))
    suggestion_types = await sync_to_async(list)(SuggestionTypeModel.objects.filter(in_use=True).values_list('name', flat=True))

    prompt = await PromptManager.read_prompt('prompt_complaint_suggestion_classifier')
    prompt_result = PromptManager.fill_out_prompt(
        prompt, {'complaint_suggestion': complaint_suggestion})

    complaint_suggestion_response = await OpenAISingleton.create_completion_message(
        system_message=system_message,
        prompt=prompt_result,)

    if complaint_suggestion_response.choices[0].message.content == 'Queja':
        prompt = await PromptManager.read_prompt('prompt_complaints')
        prompt_result = PromptManager.fill_out_prompt(
            prompt, {'complaint_types': complaint_types, 'complaint': complaint_suggestion})

        complaint_type_response = await OpenAISingleton.create_completion_message(
            system_message=system_message,
            prompt=prompt_result,)

        complaint_type = complaint_type_response.choices[0].message.content

        if complaint_type == 'Ninguno':
            complaint_type = None
        else:
            complaint_type = await sync_to_async(ComplaintTypeModel.objects.filter(name=complaint_type).first)()

        await sync_to_async(ComplaintModel.objects.create)(description=complaint_suggestion, complaint_type=complaint_type, name=name, email=email)

    else:
        prompt = await PromptManager.read_prompt('prompt_suggestions')
        prompt_result = PromptManager.fill_out_prompt(
            prompt, {'suggestion_types': suggestion_types, 'suggestion': complaint_suggestion})

        suggestion_type_response = await OpenAISingleton.create_completion_message(
            system_message=system_message,
            prompt=prompt_result,)

        suggestion_type = suggestion_type_response.choices[0].message.content

        if suggestion_type == 'Ninguno':
            suggestion_type = None
        else:
            suggestion_type = await sync_to_async(SuggestionTypeModel.objects.filter(
                name=suggestion_type).first)()

        await sync_to_async(SuggestionModel.objects.create)(description=complaint_suggestion, suggestion_type=suggestion_type, name=name, email=email)
