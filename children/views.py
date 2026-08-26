from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ChildForm
from .models import Child


class ChildListView(LoginRequiredMixin, ListView):
    template_name = 'children/list.html'
    context_object_name = 'children'

    def get_queryset(self):
        return Child.objects.filter(user=self.request.user)


class ChildCreateView(LoginRequiredMixin, CreateView):
    template_name = 'children/form.html'
    form_class = ChildForm
    success_url = reverse_lazy('children:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ChildUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'children/form.html'
    form_class = ChildForm
    success_url = reverse_lazy('children:list')

    def get_queryset(self):
        return Child.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '子供プロフィールを更新しました。')
        return response


class ChildDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'children/confirm_delete.html'
    success_url = reverse_lazy('children:list')

    def get_queryset(self):
        return Child.objects.filter(user=self.request.user)
