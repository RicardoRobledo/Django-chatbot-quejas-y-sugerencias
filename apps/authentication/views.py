from http import HTTPStatus

from asgiref.sync import sync_to_async

from django.conf import settings
from django.views import View
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache

from .forms import LoginForm
from ..users.models import UserModel


__author__ = 'Ricardo'
__version__ = '0.1'


def custom_404(request, exception):
    return render(request, 'authentication/404.html', status=404)


class LoginView(View):

    form_class = LoginForm
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('chatbot_app:chat')

    async def get(self, request, *args, **kwargs):
        """
        This method return our login view
        """
        
        response = render(request, self.template_name, {'form': self.form_class})
        return response
    

    async def post(self, request, *args, **kwargs):
        """
        This method validates the login form.
        """
        form = self.form_class(request.POST)

        is_valid = await sync_to_async(form.is_valid)()
        if not is_valid:
            return HttpResponse(content='Error, invalid form', status=HTTPStatus.BAD_REQUEST)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = await sync_to_async(authenticate)(request, username=username, password=password)
        if not user:
            return HttpResponse(content='Error, user not found', status=HTTPStatus.NOT_FOUND)

        await sync_to_async(login)(request, user)

        return JsonResponse(data={'redirect_url':self.success_url}, status=HTTPStatus.FOUND)
