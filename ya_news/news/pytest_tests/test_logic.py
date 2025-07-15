from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Проверка, что аноним не может создать комментарий."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news, author, form_data):
    """Проверка создания комментария авторизованным пользователем."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, bad_words_data):
    """Проверка валидации запрещенных слов в комментариях."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assert 'form' in response.context
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment, news):
    """Проверка удаления комментария автором."""
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    """Проверка запрета удаления чужого комментария."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment, news, form_data):
    """Проверка редактирования комментария автором."""
    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(reader_client, comment, form_data):
    """Проверка запрета редактирования чужого комментария."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
