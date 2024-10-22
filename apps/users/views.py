import json
from http import HTTPStatus

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .repositories import users_completion_suggestion_repository


@require_http_methods(["GET"])
def home_view(request):
    return render(request, 'users/user_complaints_and_suggestions.html')


@require_http_methods(["POST"])
async def create_complaint_suggestion_view(request):
    """
    This method create a new complaint or suggestion
    """

    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    complaint_suggestion = request.POST.get('complaint_suggestion', '')

    if not complaint_suggestion:
        return JsonResponse({'msg': 'Complaint or suggestion is required'}, status=HTTPStatus.BAD_REQUEST)

    await users_completion_suggestion_repository.classify_by_type(complaint_suggestion, name, email)

    return JsonResponse({'msg': 'Complaint or suggestion created successfully'}, status=HTTPStatus.CREATED)
