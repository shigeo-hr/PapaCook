from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class TopView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/top.html'
