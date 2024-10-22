from io import BytesIO
import json
from http import HTTPStatus
from functools import wraps

import pandas as pd

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from django.db.models.functions import ExtractYear
from django.conf import settings

from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton

from asgiref.sync import sync_to_async

from .repositories import complaints_and_suggestions_repository
from .models import ComplaintModel, ComplaintTypeModel, SuggestionModel, SuggestionTypeModel


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('authentication_app:custom_panel_control_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@method_decorator(login_required(login_url=settings.CUSTOM_PANEL_CONTROL_LOGIN_URL), name='dispatch')
@method_decorator(staff_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AdminHomeView(View):

    def get(self, request, *args, **kwargs):
        """
        This method returns the admin home view with complaint and suggestion years.
        """

        complaint_years = list(
            ComplaintModel.objects.annotate(year=ExtractYear(
                'created_at')).values_list('year', flat=True).distinct()
        )

        suggestion_years = list(
            SuggestionModel.objects.annotate(year=ExtractYear(
                'created_at')).values_list('year', flat=True).distinct()
        )

        years = set(complaint_years + suggestion_years)

        return render(request, 'custom_admin/complaints_and_suggestions.html', {"years": sorted(years, reverse=True)})


@method_decorator(login_required(login_url=settings.CUSTOM_PANEL_CONTROL_LOGIN_URL), name='dispatch')
@method_decorator(staff_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AdminMetricsView(View):

    async def get(self, request, *args, **kwargs):
        """
        This method returns the metrics of the complaints and suggestions.
        """

        metrics = await complaints_and_suggestions_repository.get_admin_metrics()

        return render(request, 'custom_admin/custom_metrics.html', context=metrics)


@require_http_methods(["PUT"])
async def admin_update_complaint_types_view(request):
    """
    This function update complaint types
    """

    try:
        complaints = json.loads(request.body.decode(
            'utf-8')).get('complaints', [])
    except json.JSONDecodeError:
        return JsonResponse(data={'error': 'Invalid JSON'}, status=HTTPStatus.BAD_REQUEST)

    if len(complaints) > 5:
        return JsonResponse(data={'error': 'You can only add 5 complaint types'}, status=HTTPStatus.BAD_REQUEST)

    response = await complaints_and_suggestions_repository.update_complaint_types(complaints)

    return response


@require_http_methods(["PUT"])
async def admin_update_suggestion_types_view(request):
    """
    This function update suggestion types
    """

    try:
        suggestions = json.loads(request.body.decode(
            'utf-8')).get('suggestions', [])
    except json.JSONDecodeError:
        return JsonResponse(data={'error': 'Invalid JSON'}, status=HTTPStatus.BAD_REQUEST)

    if len(suggestions) > 5:
        return JsonResponse(data={'error': 'You can only add 5 suggestion types'}, status=HTTPStatus.BAD_REQUEST)

    response = await complaints_and_suggestions_repository.update_suggestion_types(suggestions)

    return response


@require_http_methods(["GET"])
async def get_excel_file_view(request):
    """
    This function return the excel file with the complaints and suggestions
    """

    complaints = await sync_to_async(list)(ComplaintModel.objects.select_related('complaint_type').all().values(
        'id', 'description', 'complaint_type__name', 'name', 'email'
    ))

    suggestions = await sync_to_async(list)(SuggestionModel.objects.select_related('suggestion_type').all().values(
        'id', 'description', 'suggestion_type__name', 'name', 'email'
    ))

    # 2. Become the data into a DataFrame
    df_complaints = pd.DataFrame(list(complaints))
    df_suggestions = pd.DataFrame(list(suggestions))

    # Rename columns
    df_complaints.columns = ['ID', 'Descripción',
                             'Tipo de Queja', 'Nombre', 'Email']
    df_suggestions.columns = ['ID', 'Descripción',
                              'Tipo de Sugerencia', 'Nombre', 'Email']

    # 3. Create the Excel file
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Escribir los datos de quejas y sugerencias en diferentes hojas del archivo Excel
            df_complaints.to_excel(writer, sheet_name='Quejas', index=False)
            df_suggestions.to_excel(
                writer, sheet_name='Sugerencias', index=False)

        # 4. Set up the response
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=quejas_y_sugerencias.xlsx'

        return response


async def get_year_statistics_view(request, year):
    """
    This function return complaints and suggestions classified by the type with the number of them given a year

    :param year: Year
    """

    response = await complaints_and_suggestions_repository.complaints_and_suggestions_by_year(year)
    return JsonResponse(response)


async def get_statistics_by_year_and_month_view(request, year):
    """
    This function return the number of complaints and suggestions grouped by month

    :param year: Year
    """

    combined_statistics = await complaints_and_suggestions_repository.get_statistics_by_year_and_month(year)
    return JsonResponse(data={'statistics': combined_statistics}, status=HTTPStatus.OK)


async def get_statistics_month_view(request, year, month):
    """
    This function return the number of complaints and suggestions grouped by month

    :param year: Year
    :param month: Month
    """

    statistics = await complaints_and_suggestions_repository.get_statistics_month(year, month)
    return JsonResponse(data={'statistics': statistics}, status=HTTPStatus.OK)


async def get_complaints_by_year_and_type_view(request,):
    """
    This function return complaints given a year and type
    """

    name = request.GET.get('name')
    year = request.GET.get('year')
    month = request.GET.get('month', '')

    complaint_type = await sync_to_async(ComplaintTypeModel.objects.filter)(name=name,)

    if not await sync_to_async(complaint_type.exists)():
        return JsonResponse({'error': 'Invalid complaint type'}, status=HTTPStatus.BAD_REQUEST)

    complaint_type = await sync_to_async(complaint_type.first)()

    if month:
        complaints = await sync_to_async(list)(ComplaintModel.objects.filter(complaint_type=complaint_type, created_at__year=year, created_at__month=month,))
    else:
        complaints = await sync_to_async(list)(ComplaintModel.objects.filter(complaint_type=complaint_type, created_at__year=year,))

    return JsonResponse(data={'complaints': [
        {'description': complaint.description, 'name': complaint.name, 'email': complaint.email, 'year': complaint.created_at.strftime('%d-%m-%Y')} for complaint in complaints]
    }, status=HTTPStatus.OK)


async def get_suggestions_by_year_and_type_view(request,):
    """
    This function return suggestions given a year and type
    """

    name = request.GET.get('name')
    year = request.GET.get('year')
    month = request.GET.get('month', '')

    suggestion_type = await sync_to_async(SuggestionTypeModel.objects.filter)(name=name,)

    if not await sync_to_async(suggestion_type.exists)():
        return JsonResponse({'error': 'Invalid suggestion type'}, status=HTTPStatus.BAD_REQUEST)

    suggestion_type = await sync_to_async(suggestion_type.first)()

    if month:
        suggestions = await sync_to_async(list)(SuggestionModel.objects.filter(suggestion_type=suggestion_type, created_at__year=year, created_at__month=month,))
    else:
        suggestions = await sync_to_async(list)(SuggestionModel.objects.filter(suggestion_type=suggestion_type, created_at__year=year,))

    return JsonResponse(data={'suggestions': [
        {'description': suggestion.description, 'name': suggestion.name, 'email': suggestion.email, 'year': suggestion.created_at.strftime('%d-%m-%Y')} for suggestion in suggestions]
    }, status=HTTPStatus.OK)
