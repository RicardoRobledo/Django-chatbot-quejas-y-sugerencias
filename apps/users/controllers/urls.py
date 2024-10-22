from django.urls import path
from .. import views


app_name = 'users_app'


urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('complaint_suggestion/', views.create_complaint_suggestion_view,
         name="create_complaint_suggestion")
]
