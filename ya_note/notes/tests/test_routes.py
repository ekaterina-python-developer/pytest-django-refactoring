from http import HTTPStatus

from .test_mixins import (
    BaseTestData,
    HOME_URL,
    NOTE_ADD_URL,
    NOTE_DELETE_URL,
    NOTE_DETAIL_URL,
    NOTE_EDIT_URL,
    NOTE_SUCCESS_URL,
    NOTES_LIST_URL,
    LOGIN_URL,
    SIGNUP_URL,
    LOGOUT_URL,
    NOTE_EDIT_REDIRECT_URL,
    NOTE_DELETE_REDIRECT_URL
)


class TestRoutes(BaseTestData):
    """Тестирование доступности маршрутов приложения."""

    def test_routes_availability(self):
        """Тестирование доступности страниц с разными методами."""
        test_cases = [
            # Публичные GET-страницы
            ('GET', HOME_URL, self.client, HTTPStatus.OK),
            ('GET', LOGIN_URL,
             self.client, HTTPStatus.OK),
            ('GET', SIGNUP_URL,
             self.client, HTTPStatus.OK),

            # Приватные GET-страницы для автора
            ('GET', NOTE_ADD_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_DETAIL_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_EDIT_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_DELETE_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            ('GET', NOTE_SUCCESS_URL, self.author_client, HTTPStatus.OK),

            # GET-доступ для читателя (должен быть запрещён)
            (
                'GET',
                NOTE_EDIT_URL,
                self.not_author_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                'GET',
                NOTE_DELETE_URL,
                self.not_author_client,
                HTTPStatus.NOT_FOUND
            ),

            # POST-запрос (например, logout)
            ('POST', LOGOUT_URL,
             self.client, HTTPStatus.OK),

            # Перенаправления для анонимных пользователей
            ('GET', NOTE_EDIT_URL, self.client, HTTPStatus.FOUND),
            ('GET', NOTE_DELETE_URL, self.client, HTTPStatus.FOUND),
        ]

        for method, url, client, expected_status in test_cases:
            with self.subTest(method=method, url=url):
                self.assertEqual(client.generic(
                    method, url).status_code, expected_status)

    def test_redirects_for_anonymous(self):
        """Тестирование редиректов для анонимных пользователей."""
        test_cases = [
            (NOTE_EDIT_URL, NOTE_EDIT_REDIRECT_URL),
            (NOTE_DELETE_URL, NOTE_DELETE_REDIRECT_URL),
        ]

        for url, redirect_url in test_cases:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url
                )
