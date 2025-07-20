from http import HTTPStatus

from django.urls import reverse_lazy

from .test_mixins import (
    BaseTestData,
    HOME_URL,
    NOTE_ADD_URL,
    NOTE_DELETE_URL,
    NOTE_DETAIL_URL,
    NOTE_EDIT_URL,
    NOTE_SUCCESS_URL,
    NOTES_LIST_URL,
)


class TestRoutes(BaseTestData):
    """Тестирование доступности маршрутов приложения."""

    def test_routes_availability(self):
        """Тестирование доступности страниц с разными методами."""
        test_cases = [
            # Публичные GET-страницы
            ('GET', HOME_URL, self.client, HTTPStatus.OK),
            ('GET', reverse_lazy('users:login'),
             self.client, HTTPStatus.OK),
            ('GET', reverse_lazy('users:signup'),
             self.client, HTTPStatus.OK),

            # Приватные GET-страницы для автора
            ('GET', NOTE_ADD_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_DETAIL_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_EDIT_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_DELETE_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_SUCCESS_URL, self.author_client, HTTPStatus.OK),

            # GET-доступ для читателя (должен быть запрещён)
            ('GET', NOTE_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            ('GET', NOTE_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),

            # POST-запрос (например, logout)
            ('POST', reverse_lazy('users:logout'),
             self.client, HTTPStatus.OK),
        ]

        for method, url, client, expected_status in test_cases:
            with self.subTest(method=method, url=url):
                response = client.generic(method, url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous(self):
        """Тестирование редиректов для анонимных пользователей."""
        test_cases = [
            (self.NOTE_EDIT_URL, self.REDIRECT_AFTER_LOGIN['edit']),
            (self.NOTE_DELETE_URL, self.REDIRECT_AFTER_LOGIN['delete']),
        ]

        for url, redirect_url in test_cases:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url
                )
