from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, method, expected_status',
    [
        # Публичные GET-страницы
        ('home_url', 'client', 'get', HTTPStatus.OK),
        ('detail_url', 'client', 'get', HTTPStatus.OK),
        ('login_url', 'client', 'get', HTTPStatus.OK),
        ('signup_url', 'client', 'get', HTTPStatus.OK),
        # POST-запрос на logout
        ('logout_url', 'client', 'post', HTTPStatus.OK),
        # Редактирование и удаление комментариев — автор
        ('edit_url', 'author_client', 'get', HTTPStatus.OK),
        ('delete_url', 'author_client', 'get', HTTPStatus.OK),
        # Редактирование и удаление комментариев — читатель
        ('edit_url', 'reader_client', 'get', HTTPStatus.NOT_FOUND),
        ('delete_url', 'reader_client', 'get', HTTPStatus.NOT_FOUND),
    ]
)
def test_all_status_codes(
    request,
    url_fixture,
    client_fixture,
    method,
    expected_status
):
    """Проверка всех кодов возврата для страниц сайта."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = getattr(client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    [
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ]
)
def test_anonymous_redirects(client, login_url, url_fixture):
    """Редирект анонимных пользователей на страницу логина."""
    redirect_url = f'{login_url}?next={url_fixture}'
    response = client.get(url_fixture)
    assertRedirects(response, redirect_url)
