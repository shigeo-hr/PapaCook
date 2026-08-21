from django.contrib.auth import login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.views import PasswordChangeDoneView as BasePasswordChangeDoneView
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, PasswordChangeForm, SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('top')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'


class LogoutView(BaseLogoutView):
    pass


class PasswordChangeView(BasePasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')


class PasswordChangeDoneView(BasePasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'
