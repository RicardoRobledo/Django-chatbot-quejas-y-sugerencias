from django.urls import path

from .. import views


app_name = 'chatbot_app'


urlpatterns = [
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('thread_id/', views.CreateThreadView.as_view()),
    path('thread_id/<int:thread_id>/', views.DeleteThreadView.as_view()),
    path('message/', views.SendMessageView.as_view()),
]
