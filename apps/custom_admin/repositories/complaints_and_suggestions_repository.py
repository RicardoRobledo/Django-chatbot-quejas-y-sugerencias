from http import HTTPStatus
from datetime import datetime
from asgiref.sync import sync_to_async
from collections import defaultdict

from django.db.models import Count, F
from django.http import JsonResponse

from apps.desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from apps.base.utils.managers import PromptManager
from ..models import ComplaintModel, ComplaintTypeModel, SuggestionModel, SuggestionTypeModel


async def complaints_and_suggestions_by_year(year: int):

    complaint_types_in_use = await sync_to_async(list)(ComplaintTypeModel.objects.filter(in_use=True))
    suggestion_types_in_use = await sync_to_async(list)(SuggestionTypeModel.objects.filter(in_use=True))

    complaints_by_month = await sync_to_async(list)(
        ComplaintModel.objects.filter(
            created_at__year=year,
            complaint_type__name__in=complaint_types_in_use
        )
        .values('created_at__month')
        .annotate(month=F('created_at__month'), count=Count('id'))
        .values('month', 'count')
        .order_by('created_at__month')
    )

    complaints_by_type_and_year = await sync_to_async(list)(
        ComplaintModel.objects.filter(
            created_at__year=year,
            complaint_type__name__in=complaint_types_in_use
        )
        .values('complaint_type__name')
        .annotate(type=F('complaint_type__name'), count=Count('id'))
        .values('type', 'count')
        .order_by('count')
    )

    suggestions_by_month = await sync_to_async(list)(
        SuggestionModel.objects.filter(
            created_at__year=year,
            suggestion_type__name__in=suggestion_types_in_use
        )
        .values('created_at__month')
        .annotate(month=F('created_at__month'), count=Count('id'))
        .values('month', 'count')
        .order_by('created_at__month')
    )

    suggestions_by_type_and_year = await sync_to_async(list)(
        SuggestionModel.objects.filter(
            created_at__year=year,
            suggestion_type__name__in=suggestion_types_in_use
        )
        .values('suggestion_type__name')
        .annotate(type=F('suggestion_type__name'), count=Count('id'))
        .values('type', 'count')
        .order_by('count')
    )

    print({'complaints_by_month': complaints_by_month,
           'complaints_by_type_and_year': complaints_by_type_and_year,
           'suggestions_by_month': suggestions_by_month,
           'suggestions_by_type_and_year': suggestions_by_type_and_year, })

    return {'complaints_by_month': complaints_by_month,
            'complaints_by_type_and_year': complaints_by_type_and_year,
            'suggestions_by_month': suggestions_by_month,
            'suggestions_by_type_and_year': suggestions_by_type_and_year, }


async def get_statistics_month(year: int, month: int):
    """
    This function return complaints and suggestions of a specific month

    :param year: Year
    :param month: Month
    """

    complaint_types_in_use = await sync_to_async(list)(ComplaintTypeModel.objects.filter(in_use=True))
    suggestion_types_in_use = await sync_to_async(list)(SuggestionTypeModel.objects.filter(in_use=True))

    complaint_statistics = await sync_to_async(list)(
        ComplaintModel.objects.filter(
            created_at__year=year,
            created_at__month=month,
            complaint_type__name__in=complaint_types_in_use
        )
        .values('complaint_type__name')
        .annotate(type=F('complaint_type__name'), count=Count('id'))
        .values('type', 'count')
        .order_by('-count')
    )

    suggestion_statistics = await sync_to_async(list)(
        SuggestionModel.objects.filter(
            created_at__year=year,
            created_at__month=month,
            suggestion_type__name__in=suggestion_types_in_use
        )
        .values('suggestion_type__name')
        .annotate(type=F('suggestion_type__name'), count=Count('id'))
        .values('type', 'count')
        .order_by('-count')
    )

    return {'complaint_statistics': complaint_statistics, 'suggestion_statistics': suggestion_statistics}


async def update_complaint_types(complaints):
    """
    This function updates complaint types asynchronously.
    """

    # Obtener las quejas existentes y que están en uso actualmente
    existing_complaints_in_use = await sync_to_async(list)(
        ComplaintTypeModel.objects.filter(
            name__in=complaints, in_use=True).values_list('name', flat=True)
    )
    existing_complaints_in_use = set(existing_complaints_in_use)

    # Obtener las quejas existentes, pero que están desactivadas (in_use=False)
    existing_complaints_not_in_use = await sync_to_async(list)(
        ComplaintTypeModel.objects.filter(
            name__in=complaints, in_use=False).values_list('name', flat=True)
    )
    existing_complaints_not_in_use = set(existing_complaints_not_in_use)

    # Quejas que faltan en la base de datos (no existen)
    missing_complaints = [
        complaint for complaint in complaints
        if complaint not in existing_complaints_in_use and complaint not in existing_complaints_not_in_use
    ]

    # Activar las quejas que están desactivadas (in_use=False)
    if existing_complaints_not_in_use:
        await sync_to_async(ComplaintTypeModel.objects.filter(name__in=existing_complaints_not_in_use).update)(in_use=True)

    # Crear las nuevas quejas que no existen en la base de datos
    if missing_complaints:
        await sync_to_async(ComplaintTypeModel.objects.bulk_create)(
            [ComplaintTypeModel(name=complaint, in_use=True)
             for complaint in missing_complaints]
        )

    # Desactivar las quejas que ya no están en la lista proporcionada y están activas
    complaints_to_deactivate = await sync_to_async(list)(
        ComplaintTypeModel.objects.filter(in_use=True).exclude(
            name__in=complaints).values_list('name', flat=True)
    )
    if complaints_to_deactivate:
        await sync_to_async(ComplaintTypeModel.objects.filter(name__in=complaints_to_deactivate).update)(in_use=False)

    # Devolver un mensaje adecuado sobre el resultado de la operación
    if not missing_complaints and not existing_complaints_not_in_use and not complaints_to_deactivate:
        return JsonResponse({'msg': 'All complaints are already up-to-date'}, status=HTTPStatus.OK)
    else:
        return JsonResponse({'msg': 'Complaints updated or created as needed'}, status=HTTPStatus.CREATED)


async def update_suggestion_types(suggestions):
    """
    This function update suggestion types
    """

    # Obtener las quejas existentes y que están en uso actualmente
    existing_suggestions_in_use = await sync_to_async(list)(
        SuggestionTypeModel.objects.filter(
            name__in=suggestions, in_use=True).values_list('name', flat=True)
    )
    existing_suggestions_in_use = set(existing_suggestions_in_use)

    # Obtener las quejas existentes, pero que están desactivadas (in_use=False)
    existing_suggestions_not_in_use = await sync_to_async(list)(
        SuggestionTypeModel.objects.filter(
            name__in=suggestions, in_use=False).values_list('name', flat=True)
    )
    existing_suggestions_not_in_use = set(existing_suggestions_not_in_use)

    # Quejas que faltan en la base de datos (no existen)
    missing_suggestions = [
        suggestion for suggestion in suggestions
        if suggestion not in existing_suggestions_in_use and suggestion not in existing_suggestions_not_in_use
    ]

    # Activar las quejas que están desactivadas (in_use=False)
    if existing_suggestions_not_in_use:
        await sync_to_async(SuggestionTypeModel.objects.filter(name__in=existing_suggestions_not_in_use).update)(in_use=True)

    # Crear las nuevas quejas que no existen en la base de datos
    if missing_suggestions:
        await sync_to_async(SuggestionTypeModel.objects.bulk_create)(
            [SuggestionTypeModel(name=suggestion, in_use=True)
             for suggestion in missing_suggestions]
        )

    # Desactivar las quejas que ya no están en la lista proporcionada y están activas
    suggestions_to_deactivate = await sync_to_async(list)(
        SuggestionTypeModel.objects.filter(in_use=True).exclude(
            name__in=suggestions).values_list('name', flat=True)
    )
    if suggestions_to_deactivate:
        await sync_to_async(SuggestionTypeModel.objects.filter(name__in=suggestions_to_deactivate).update)(in_use=False)

    # Devolver un mensaje adecuado sobre el resultado de la operación
    if not missing_suggestions and not existing_suggestions_not_in_use and not suggestions_to_deactivate:
        return JsonResponse({'msg': 'All suggestions are already up-to-date'}, status=HTTPStatus.OK)
    else:
        return JsonResponse({'msg': 'Suggestionss updated or created as needed'}, status=HTTPStatus.CREATED)


async def get_admin_metrics():
    """
    This function return the suggestions types and complaint types in use
    """

    complaint_types = await sync_to_async(list)(ComplaintTypeModel.objects.filter(in_use=True).values_list('name', flat=True))
    suggestion_types = await sync_to_async(list)(SuggestionTypeModel.objects.filter(in_use=True).values_list('name', flat=True))

    return {'complaint_types': complaint_types, 'suggestion_types': suggestion_types}


async def get_statistics_by_year_and_month(year: int):
    """
    This function return the number of complaints and suggestions grouped by existent month

    :param year: Year
    """

    complaint_types_in_use = await sync_to_async(list)(ComplaintTypeModel.objects.filter(in_use=True))
    suggestion_types_in_use = await sync_to_async(list)(SuggestionTypeModel.objects.filter(in_use=True))

    complaint_statistics = await sync_to_async(list)(
        ComplaintModel.objects
        .filter(created_at__year=year, complaint_type__name__in=complaint_types_in_use)
        .values('created_at__month')
        .annotate(month=F('created_at__month'), count=Count('id'))
        .values('month', 'count')
        .order_by('created_at__month'))

    suggestion_statistics = await sync_to_async(list)(
        SuggestionModel.objects
        .filter(created_at__year=year, suggestion_type__name__in=suggestion_types_in_use)
        .values('created_at__month')
        .annotate(month=F('created_at__month'), count=Count('id'))
        .values('month', 'count')
        .order_by('created_at__month'))

    combined_statistics = defaultdict(int)

    for item in complaint_statistics:
        combined_statistics[item['month']] += item['count']

    for item in suggestion_statistics:
        combined_statistics[item['month']] += item['count']

    combined_statistics = [{'month': month, 'count': count}
                           for month, count in sorted(combined_statistics.items())]

    return combined_statistics
