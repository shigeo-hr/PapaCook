from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TopViewTest(TestCase):
    def setUp(self):
        self.url = reverse('top')

    def test_unauthenticated_shows_landing_page(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/landing.html')

    def test_authenticated_shows_top_page(self):
        user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/top.html')
