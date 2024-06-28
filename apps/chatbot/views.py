import json

from asgiref.sync import sync_to_async

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse

from ..desing_patterns.creational_patterns.singleton.openai_singleton import OpenAISingleton
from .repositories import chatbot_repository


@method_decorator(require_http_methods(["POST"]), name='dispatch')
class SendMessageView(View):

    async def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        thread_id = body.get('thread_id')
        user_message = body.get('user_message')
        dates = body.get('dates')
        
        response = await chatbot_repository.send_message(dates, thread_id, user_message)
        return JsonResponse(data=response['data'], status=response['status_code'])


@method_decorator(require_http_methods(["GET"]), name='dispatch')
class CreateThreadView(View):

    async def get(self, request, *args, **kwargs):
        OpenAISingleton()
        thread_id =  await OpenAISingleton.create_thread()
        return JsonResponse({'thread_id':thread_id.id})


@method_decorator(require_http_methods(["POST"]), name='dispatch')
class DeleteThreadView(View):
    
    async def post(self, request, thread_id, *args, **kwargs):
        await OpenAISingleton.delete_thread(thread_id)
        return JsonResponse({})


@method_decorator(login_required(login_url=settings.LOGIN_URL), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ChatView(View):

    def get(self, request, *args, **kwargs):
        """
        This method return our chatbot view
        """
        
        return TemplateResponse(request, 'chatbot/chat.html')
