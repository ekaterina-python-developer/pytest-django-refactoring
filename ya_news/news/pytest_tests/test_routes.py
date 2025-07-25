from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

# Константы статусов
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND

# Константы для клиентов
ANONYMOUS_CLIENT = lf('client')
AUTHOR_CLIENT = lf('author_client')
READER_CLIENT = lf('reader_client')

# Константы URL
HOME_URL = lf('home_url')
DETAIL_URL = lf('detail_url')
LOGIN_URL = lf('login_url')
SIGNUP_URL = lf('signup_url')
LOGOUT_URL = lf('logout_url')
EDIT_URL = lf('edit_url')
DELETE_URL = lf('delete_url')
EDIT_REDIRECT_URL = lf('edit_redirect_url')
DELETE_REDIRECT_URL = lf('delete_redirect_url')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, test_client, method, expected_status',
    [
        # Публичные GET-страницы
        (HOME_URL, ANONYMOUS_CLIENT, 'get', OK),
        (DETAIL_URL, ANONYMOUS_CLIENT, 'get', OK),
        (LOGIN_URL, ANONYMOUS_CLIENT, 'get', OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, 'get', OK),

        # POST-запрос на logout
        (LOGOUT_URL, ANONYMOUS_CLIENT, 'post', OK),

        # Приватные страницы для автора
        (EDIT_URL, AUTHOR_CLIENT, 'get', OK),
        (DELETE_URL, AUTHOR_CLIENT, 'get', OK),

        # Запрещённые страницы для читателя
        (EDIT_URL, READER_CLIENT, 'get', NOT_FOUND),
        (DELETE_URL, READER_CLIENT, 'get', NOT_FOUND),

        # Редиректы для анонимов
        (EDIT_URL, ANONYMOUS_CLIENT, 'get', FOUND),
        (DELETE_URL, ANONYMOUS_CLIENT, 'get', FOUND),
    ]
)
def test_status_codes(url, test_client, method, expected_status):
    """Проверка кодов состояния для всех маршрутов."""
    response = getattr(test_client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, redirect_url',
    [
        (lf('edit_url'), lf('edit_redirect_url')),
        (lf('delete_url'), lf('delete_redirect_url')),
    ]
)
def test_anonymous_redirects(client, url, redirect_url):
    """Проверка редиректов для неавторизованных пользователей."""
    response = client.get(url)
    assertRedirects(response, redirect_url)
