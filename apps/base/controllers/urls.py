from django.urls import path
from ...base import views


app_name = 'base_app'


urlpatterns = [
    path('admin/custom-view/', views.custom_admin_view, name='custom_admin_view'),
    path('admin/statistics/', views.FullStatisticsView.as_view(),
         name='statistics_view'),
    path('admin/statistics/<str:month>/', views.MonthStatisticsView.as_view(),
         name='month_statistics_view'),
]
