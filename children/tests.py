from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Child

User = get_user_model()


class ChildModelTest(TestCase):
    def test_str_returns_name(self):
        user = User.objects.create_user(
            username='parent', email='parent@example.com', password='TestPass12345',
        )
        child = Child.objects.create(user=user, name='たろう', age=7)
        self.assertEqual(str(child), 'たろう')


class ChildListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='TestPass12345',
        )
        self.url = reverse('children:list')

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_shows_only_own_children(self):
        Child.objects.create(user=self.user, name='たろう', age=7)
        Child.objects.create(user=self.other_user, name='はなこ', age=5)

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        names = [child.name for child in response.context['children']]
        self.assertEqual(names, ['たろう'])


class ChildCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.url = reverse('children:create')

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_valid_submission_creates_child_owned_by_current_user(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'name': 'たろう',
            'age': 7,
            'likes': 'カレー',
            'dislikes': 'ピーマン',
            'allergies': '卵',
        })

        self.assertRedirects(response, reverse('children:list'))
        child = Child.objects.get(name='たろう')
        self.assertEqual(child.user, self.user)
        self.assertEqual(child.dislikes, 'ピーマン')
        self.assertEqual(child.allergies, '卵')

    def test_missing_required_fields_shows_validation_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'name': '', 'age': ''})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'name', 'このフィールドは必須です。')
        self.assertFormError(response.context['form'], 'age', 'このフィールドは必須です。')
        self.assertFalse(Child.objects.exists())


class ChildUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='TestPass12345',
        )
        self.child = Child.objects.create(user=self.user, name='たろう', age=7)
        self.url = reverse('children:update', kwargs={'pk': self.child.pk})

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_other_users_child_returns_404(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_valid_submission_updates_child_and_shows_message(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {
            'name': 'たろう',
            'age': 8,
            'likes': '',
            'dislikes': 'なす',
            'allergies': '',
        }, follow=True)

        self.child.refresh_from_db()
        self.assertEqual(self.child.age, 8)
        self.assertEqual(self.child.dislikes, 'なす')
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), '子供プロフィールを更新しました。')


class ChildDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass12345',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='TestPass12345',
        )
        self.child = Child.objects.create(user=self.user, name='たろう', age=7)
        self.url = reverse('children:delete', kwargs={'pk': self.child.pk})

    def test_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_get_renders_confirmation_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children/confirm_delete.html')
        self.assertTrue(Child.objects.filter(pk=self.child.pk).exists())

    def test_other_users_child_returns_404(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_post_deletes_child_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('children:list'))
        self.assertFalse(Child.objects.filter(pk=self.child.pk).exists())

    def test_other_user_cannot_delete_via_post(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Child.objects.filter(pk=self.child.pk).exists())
