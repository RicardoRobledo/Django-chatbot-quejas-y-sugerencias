import json
from http import HTTPStatus

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
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


class YearStatisticsView(View):

    async def post(self, request, *args, **kwargs):
        """
        This method return a completion given a year
        """

        data = json.loads(request.body)
        year = data.get('year')

        response = await completions_repository.completion_by_year(year)
        return JsonResponse(response)


class YearMonthStatisticsView(View):

    async def post(self, request, *args, **kwargs):
        """
        This method return a completion given a month and year
        """

        try:

            data = json.loads(request.body)
            month = data.get('month')
            year = data.get('year')

            response = await completions_repository.completion_by_month_year(int(month), int(year))
            return JsonResponse(response, status=HTTPStatus.OK)

        except ValueError:
            return JsonResponse({'error': 'Invalid month'}, status=HTTPStatus.BAD_REQUEST)
