from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .dummy_data import get_dummy_recipe, get_dummy_recipes
from .forms import RecipeConditionForm

CONDITIONS_SESSION_KEY = 'recipe_conditions'


class RecipeConditionView(LoginRequiredMixin, FormView):
    template_name = 'recipes/conditions.html'
    form_class = RecipeConditionForm
    success_url = reverse_lazy('recipes:list')

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('ingredients'):
            return redirect('ingredients:input')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session[CONDITIONS_SESSION_KEY] = {
            'for_kids': form.cleaned_data['for_kids'],
            'quick': form.cleaned_data['quick'],
        }
        return super().form_valid(form)


class RecipeListView(LoginRequiredMixin, TemplateView):
    template_name = 'recipes/list.html'

    def dispatch(self, request, *args, **kwargs):
        if CONDITIONS_SESSION_KEY not in request.session:
            return redirect('recipes:conditions')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conditions = self.request.session[CONDITIONS_SESSION_KEY]
        context['recipes'] = get_dummy_recipes(**conditions)
        context['conditions'] = conditions
        return context


class RecipeDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'recipes/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = get_dummy_recipe(kwargs['pk'])
        if recipe is None:
            raise Http404('レシピが見つかりません。')
        context['recipe'] = recipe
        return context
