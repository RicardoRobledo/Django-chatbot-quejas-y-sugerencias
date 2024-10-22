from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


app_name = 'authentication_app'


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('custom-panel-control-login/',
         views.CustomPanelControlLoginView.as_view(), name='custom_panel_control_login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
