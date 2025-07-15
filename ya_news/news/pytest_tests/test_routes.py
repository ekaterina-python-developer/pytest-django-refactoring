from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:signup', None),
    ]
)
def test_get_pages_availability(client, name, args):
    """Проверка доступности публичных страниц для GET-запросов."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout_page_availability(client):
    """Проверка доступности страницы выхода для POST-запросов."""
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ],
)
@pytest.mark.parametrize(
    'name',
    ['news:edit', 'news:delete'],
)
def test_comment_edit_delete_access(
    parametrized_client, name, comment_id_for_args, expected_status
):
    """Проверка прав доступа к страницам редактирования и удаления комментариев."""
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ['news:edit', 'news:delete'],
)
def test_anonymous_redirect(client, name, comment_id_for_args):
    """Проверка редиректа анонимных пользователей на страницу входа."""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
