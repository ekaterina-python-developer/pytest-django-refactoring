from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование доступности маршрутов приложения."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых пользователей и заметки."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author
        )

    def test_pages_availability(self):
        """Тестирование доступности публичных и приватных страниц."""
        public_urls = [
            ('notes:home', None, 'get'),
            ('users:login', None, 'get'),
            ('users:logout', None, 'post'),
            ('users:signup', None, 'get'),
        ]
        self._test_urls(public_urls)

        private_urls = [
            ('notes:add', None, 'get'),
            ('notes:detail', (self.note.slug,), 'get'),
            ('notes:edit', (self.note.slug,), 'get'),
            ('notes:delete', (self.note.slug,), 'get'),
            ('notes:list', None, 'get'),
            ('notes:success', None, 'get'),
        ]
        self._test_urls(private_urls, user=self.author)

    def _test_urls(self, urls, user=None):
        """Вспомогательный метод для проверки доступности URL."""
        if user:
            self.client.force_login(user)

        for name, args, method in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(
                    url) if method == 'get' else self.client.post(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        if user:
            self.client.logout()

    def test_availability_for_note_edit_and_delete(self):
        """Тестирование доступности редактирования/удаления."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тестирование редиректа анонимного пользователя на страницу входа."""
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
