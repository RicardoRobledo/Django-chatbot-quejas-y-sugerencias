from django.urls import path
from ...base import views


app_name = 'base_app'


urlpatterns = [
    path('admin/custom-view/', views.custom_admin_view, name='custom_admin_view'),
    path('admin/statistics/', views.YearStatisticsView.as_view(),
         name='year_statistics_view'),
    path('admin/statistics/month-year/', views.YearMonthStatisticsView.as_view(),
         name='month_year_statistics_view'),
]
