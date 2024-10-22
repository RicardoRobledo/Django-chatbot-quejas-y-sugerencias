from django.urls import path
from .. import views


app_name = 'custom_admin_app'


urlpatterns = [
    # General views
    path('admin/home/', views.AdminHomeView.as_view(), name='admin_home_view'),
    path('admin/metrics/', views.AdminMetricsView.as_view(),
         name='admin_metrics_view'),
    path('admin/download-excel-file/', views.get_excel_file_view,
         name='admin_download_excel_view'),
    path('admin/update_complaint_types_view/', views.admin_update_complaint_types_view,
         name='admin_update_complaint_types_view'),
    path('admin/update_suggestion_types_view/', views.admin_update_suggestion_types_view,
         name='admin_update_suggestion_types_view'),

    # Complaints and suggestions statistics
    path('admin/statistics/<int:year>/', views.get_year_statistics_view,
         name='year_statistics_view'),
    path('admin/statistics/year-month/<int:year>/', views.get_statistics_by_year_and_month_view,
         name='statistics_year_and_month_view'),
    path('admin/statistics/year-month/<int:year>/<int:month>/', views.get_statistics_month_view,
         name='statistics_month_view'),

    # Specific complaints and suggestions
    path('admin/specific-complaints/', views.get_complaints_by_year_and_type_view,
         name='complaints_year_type_view'),
    path('admin/specific-suggestions/', views.get_suggestions_by_year_and_type_view,
         name='suggestions_year_type_view'),
]
