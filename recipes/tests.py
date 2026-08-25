from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


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

    def test_valid_submission_saves_conditions_and_redirects_to_list(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['ingredients'] = ['豚肉', '玉ねぎ']
        session.save()

        response = self.client.post(self.url, {'for_kids': 'on', 'quick': ''})

        self.assertRedirects(response, reverse('recipes:list'))
        self.assertEqual(
            self.client.session['recipe_conditions'],
            {'for_kids': True, 'quick': False},
        )


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

    def test_redirects_to_conditions_when_no_conditions_in_session(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('recipes:conditions'))

    def test_filters_recipes_by_conditions(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['recipe_conditions'] = {'for_kids': True, 'quick': True}
        session.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for recipe in response.context['recipes']:
            self.assertTrue(recipe['for_kids'])
            self.assertTrue(recipe['quick'])


class RecipeDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )

    def test_redirects_to_login_when_not_authenticated(self):
        url = reverse('recipes:detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_shows_materials_and_steps_for_existing_recipe(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recipes:detail', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['recipe']['materials'])
        self.assertTrue(response.context['recipe']['steps'])

    def test_returns_404_for_unknown_recipe(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recipes:detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)
