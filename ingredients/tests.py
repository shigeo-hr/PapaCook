from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Ingredient

User = get_user_model()


class IngredientModelTest(TestCase):
    def test_str_returns_name(self):
        ingredient = Ingredient.objects.create(name='トマト', category='野菜')
        self.assertEqual(str(ingredient), 'トマト')

    def test_seed_data_migration_applied(self):
        self.assertTrue(Ingredient.objects.exists())


class IngredientInputViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.url = reverse('ingredients:input')

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_get_renders_form_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ingredients/input.html')

    def test_valid_submission_saves_names_to_session_and_redirects(self):
        self.client.force_login(self.user)
        ingredient = Ingredient.objects.create(name='パン', category='主食')

        response = self.client.post(self.url, {
            'common_ingredients': [ingredient.pk],
            'other_ingredients': 'きのこ, ほうれん草',
        })

        self.assertRedirects(response, reverse('top'))
        self.assertEqual(
            self.client.session['ingredients'],
            ['パン', 'きのこ', 'ほうれん草'],
        )

    def test_empty_submission_shows_validation_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'other_ingredients': ''})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'], None, '食材を1つ以上入力または選択してください。',
        )
        self.assertNotIn('ingredients', self.client.session)
