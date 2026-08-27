import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import DetailView, FormView, ListView

from ingredients.models import Ingredient

from .forms import RecipeConditionForm
from .models import Condition, Recipe, RecipeCondition, RecipeIngredient
from .services import RecipeGenerationError, extract_excluded_ingredients, generate_recipes

logger = logging.getLogger(__name__)

INGREDIENTS_SESSION_KEY = 'ingredients'
CONDITIONS_SESSION_KEY = 'recipe_conditions'
RESULT_SESSION_KEY = 'recipe_result_ids'

RECIPE_COUNT = 3


class RecipeConditionView(LoginRequiredMixin, FormView):
    template_name = 'recipes/conditions.html'
    form_class = RecipeConditionForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.session.get(INGREDIENTS_SESSION_KEY):
            return redirect('ingredients:input')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        for_kids = form.cleaned_data['for_kids']
        quick = form.cleaned_data['quick']
        ingredient_names = self.request.session[INGREDIENTS_SESSION_KEY]
        excluded_ingredients = extract_excluded_ingredients(self.request.user.children.all())

        try:
            generated = generate_recipes(
                ingredient_names=ingredient_names,
                for_kids=for_kids,
                quick=quick,
                excluded_ingredients=excluded_ingredients,
                count=RECIPE_COUNT,
            )
            recipe_ids = self._save_recipes(generated)
        except RecipeGenerationError:
            logger.exception('レシピ生成に失敗しました。')
            messages.error(self.request, 'レシピの提案に失敗しました。もう一度お試しください。')
            return self.render_to_response(self.get_context_data(form=form))

        self.request.session[CONDITIONS_SESSION_KEY] = {'for_kids': for_kids, 'quick': quick}
        self.request.session[RESULT_SESSION_KEY] = recipe_ids
        return redirect('recipes:list')

    @transaction.atomic
    def _save_recipes(self, generated_recipes):
        recipe_ids = []
        for item in generated_recipes:
            recipe = Recipe.objects.create(
                user=self.request.user,
                title=item['title'],
                instructions=self._build_instructions(item['steps']),
            )

            for material_name in item['materials']:
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=material_name, defaults={'category': 'その他'},
                )
                RecipeIngredient.objects.get_or_create(recipe=recipe, ingredient=ingredient)

            condition_names = []
            if item['for_kids']:
                condition_names.append('子供向け')
            if item['quick']:
                condition_names.append('時短')
            for condition_name in condition_names:
                condition, _ = Condition.objects.get_or_create(name=condition_name)
                RecipeCondition.objects.get_or_create(recipe=recipe, condition=condition)

            recipe_ids.append(recipe.pk)
        return recipe_ids

    @staticmethod
    def _build_instructions(steps):
        return '\n'.join(f'{index}. {step}' for index, step in enumerate(steps, start=1))


class RecipeListView(LoginRequiredMixin, ListView):
    template_name = 'recipes/list.html'
    context_object_name = 'recipes'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and RESULT_SESSION_KEY not in request.session:
            return redirect('recipes:conditions')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        recipe_ids = self.request.session[RESULT_SESSION_KEY]
        return (
            Recipe.objects.filter(pk__in=recipe_ids, user=self.request.user)
            .prefetch_related('conditions')
        )


class RecipeDetailView(LoginRequiredMixin, DetailView):
    template_name = 'recipes/detail.html'
    context_object_name = 'recipe'

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user).prefetch_related('ingredients')
