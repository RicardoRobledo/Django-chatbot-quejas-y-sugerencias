from http import HTTPStatus

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views import View

from apps.base.utils.managers import GoogleSheetManager
from .repositories import completions_repository
from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton

from asgiref.sync import sync_to_async, async_to_sync


@sync_to_async
@staff_member_required
@async_to_sync
async def custom_admin_view(request):

    return render(request, 'admin/complaints_and_suggestions.html')


class FullStatisticsView(View):

    async def get(self, request, *args, **kwargs):
        """
        This method return the full completion view
        """

        response = await completions_repository.full_completion()
        return JsonResponse(response)


class MonthStatisticsView(View):

    async def get(self, request, month, *args, **kwargs):
        """
        This method return a completion given a month
        """

        try:

            month = int(month)
            response = await completions_repository.completion_by_month(int(month))
            return JsonResponse(response, status=HTTPStatus.OK)

        except ValueError:
            return JsonResponse({'error': 'Invalid month'}, status=HTTPStatus.BAD_REQUEST)
