import json
from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from openai import APIConnectionError

from children.models import Child
from ingredients.models import Ingredient

from .models import Recipe
from .services import RecipeGenerationError, extract_excluded_ingredients, generate_recipes

User = get_user_model()

SAMPLE_GENERATED_RECIPES = [
    {
        'title': '豚肉と野菜の甘辛炒め',
        'for_kids': True,
        'quick': True,
        'materials': ['豚肉', '玉ねぎ', '醤油'],
        'steps': ['野菜を切る。', '炒める。', '味付けする。'],
    },
    {
        'title': '鶏肉と根菜の煮物',
        'for_kids': True,
        'quick': False,
        'materials': ['鶏肉', 'じゃがいも'],
        'steps': ['切る。', '煮込む。'],
    },
    {
        'title': 'トマトと卵の中華風炒め',
        'for_kids': False,
        'quick': True,
        'materials': ['トマト', 'たまご'],
        'steps': ['卵を炒める。', 'トマトを加える。'],
    },
]


def _mock_completion(content):
    message = MagicMock(content=content)
    choice = MagicMock(message=message)
    return MagicMock(choices=[choice])


class ExtractExcludedIngredientsTest(TestCase):
    def test_combines_and_dedupes_allergies_and_dislikes_across_children(self):
        user = User.objects.create_user(username='u', email='u@example.com', password='TestPass12345')
        Child.objects.create(user=user, name='たろう', age=7, allergies='卵、小麦', dislikes='ピーマン')
        Child.objects.create(user=user, name='はなこ', age=5, allergies='卵', dislikes='トマト、ピーマン')

        result = extract_excluded_ingredients(user.children.all())

        self.assertEqual(result, ['卵', '小麦', 'ピーマン', 'トマト'])

    def test_returns_empty_list_when_no_children(self):
        user = User.objects.create_user(username='u2', email='u2@example.com', password='TestPass12345')
        self.assertEqual(extract_excluded_ingredients(user.children.all()), [])


class GenerateRecipesTest(TestCase):
    @patch('recipes.services.OpenAI')
    def test_returns_parsed_recipes_on_success(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps({'recipes': SAMPLE_GENERATED_RECIPES})
        )

        result = generate_recipes(
            ingredient_names=['豚肉'], for_kids=True, quick=True, excluded_ingredients=[], count=3,
        )

        self.assertEqual(result, SAMPLE_GENERATED_RECIPES)

    @patch('recipes.services.OpenAI')
    def test_raises_when_recipe_count_does_not_match(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps({'recipes': SAMPLE_GENERATED_RECIPES[:2]})
        )

        with self.assertRaises(RecipeGenerationError):
            generate_recipes(
                ingredient_names=['豚肉'], for_kids=False, quick=False, excluded_ingredients=[], count=3,
            )

    @patch('recipes.services.OpenAI')
    def test_raises_when_response_is_not_valid_json(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.return_value = _mock_completion('not json')

        with self.assertRaises(RecipeGenerationError):
            generate_recipes(
                ingredient_names=['豚肉'], for_kids=False, quick=False, excluded_ingredients=[], count=3,
            )

    @patch('recipes.services.OpenAI')
    def test_raises_recipe_generation_error_when_openai_call_errors(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        request = httpx.Request('POST', 'https://api.openai.com/v1/chat/completions')
        mock_client.chat.completions.create.side_effect = APIConnectionError(request=request)

        with self.assertRaises(RecipeGenerationError):
            generate_recipes(
                ingredient_names=['豚肉'], for_kids=False, quick=False, excluded_ingredients=[], count=3,
            )


class RecipeConditionViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.url = reverse('recipes:conditions')

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_redirects_to_ingredient_input_when_no_ingredients_in_session(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('ingredients:input'))

    def test_get_renders_form_when_ingredients_in_session(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['ingredients'] = ['豚肉', '玉ねぎ']
        session.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/conditions.html')

    @patch('recipes.views.generate_recipes')
    def test_valid_submission_saves_recipes_and_redirects_to_list(self, mock_generate):
        mock_generate.return_value = SAMPLE_GENERATED_RECIPES
        self.client.force_login(self.user)
        session = self.client.session
        session['ingredients'] = ['豚肉', '玉ねぎ']
        session.save()

        response = self.client.post(self.url, {'for_kids': 'on', 'quick': ''})

        self.assertRedirects(response, reverse('recipes:list'))
        self.assertEqual(Recipe.objects.filter(user=self.user).count(), 3)
        self.assertEqual(
            self.client.session['recipe_conditions'],
            {'for_kids': True, 'quick': False},
        )

        recipe = Recipe.objects.get(title='豚肉と野菜の甘辛炒め')
        self.assertEqual(
            set(recipe.ingredients.values_list('name', flat=True)),
            {'豚肉', '玉ねぎ', '醤油'},
        )
        self.assertEqual(
            set(recipe.conditions.values_list('name', flat=True)),
            {'子供向け', '時短'},
        )
        self.assertIn('1. 野菜を切る。', recipe.instructions)
        self.assertFalse(recipe.is_favorite)

    @patch('recipes.views.generate_recipes')
    def test_calls_generate_recipes_with_excluded_ingredients_from_children(self, mock_generate):
        mock_generate.return_value = SAMPLE_GENERATED_RECIPES
        Child.objects.create(user=self.user, name='たろう', age=7, allergies='卵', dislikes='ピーマン')
        self.client.force_login(self.user)
        session = self.client.session
        session['ingredients'] = ['豚肉']
        session.save()

        self.client.post(self.url, {'for_kids': '', 'quick': ''})

        _, kwargs = mock_generate.call_args
        self.assertEqual(set(kwargs['excluded_ingredients']), {'卵', 'ピーマン'})
        self.assertEqual(kwargs['count'], 3)

    @patch('recipes.views.generate_recipes')
    def test_api_failure_shows_error_and_stays_on_conditions_page(self, mock_generate):
        mock_generate.side_effect = RecipeGenerationError('failed')
        self.client.force_login(self.user)
        session = self.client.session
        session['ingredients'] = ['豚肉']
        session.save()

        response = self.client.post(self.url, {'for_kids': '', 'quick': ''})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/conditions.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'レシピの提案に失敗しました。もう一度お試しください。')
        self.assertFalse(Recipe.objects.exists())
        self.assertNotIn('recipe_result_ids', self.client.session)


class RecipeListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.url = reverse('recipes:list')

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_redirects_to_conditions_when_no_result_in_session(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['ingredients'] = ['豚肉']
        session.save()

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('recipes:conditions'))

    def test_shows_only_own_recipes_from_latest_result(self):
        self.client.force_login(self.user)
        recipe = Recipe.objects.create(user=self.user, title='たろうの一品', instructions='1. 焼く。')
        other_user = User.objects.create_user(
            username='other', email='other@example.com', password='TestPass12345',
        )
        other_recipe = Recipe.objects.create(user=other_user, title='他人のレシピ', instructions='1. 煮る。')

        session = self.client.session
        session['recipe_result_ids'] = [recipe.pk, other_recipe.pk]
        session.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        titles = [r.title for r in response.context['recipes']]
        self.assertEqual(titles, ['たろうの一品'])


class RecipeDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='TestPass12345',
        )
        self.recipe = Recipe.objects.create(user=self.user, title='たろうの一品', instructions='1. 焼く。')

    def test_redirects_to_login_when_not_authenticated(self):
        url = reverse('recipes:detail', kwargs={'pk': self.recipe.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_shows_ingredients_and_instructions(self):
        ingredient, _ = Ingredient.objects.get_or_create(name='豚肉', defaults={'category': '肉'})
        self.recipe.ingredients.add(ingredient)
        self.client.force_login(self.user)

        response = self.client.get(reverse('recipes:detail', kwargs={'pk': self.recipe.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '豚肉')
        self.assertContains(response, '焼く')

    def test_other_users_recipe_returns_404(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('recipes:detail', kwargs={'pk': self.recipe.pk}))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_unknown_recipe(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recipes:detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)
