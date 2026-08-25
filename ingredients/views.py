from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import IngredientInputForm

SESSION_KEY = 'ingredients'


class IngredientInputView(LoginRequiredMixin, FormView):
    template_name = 'ingredients/input.html'
    form_class = IngredientInputForm
    success_url = reverse_lazy('recipes:conditions')

    def form_valid(self, form):
        self.request.session[SESSION_KEY] = form.get_ingredient_names()
        return super().form_valid(form)
