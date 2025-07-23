import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from news.forms import WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    """Проверка, что аноним не может создать комментарий."""
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, news, author, form_data, detail_url, url_to_comments
):
    """Проверка создания комментария авторизованным пользователем."""
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert (comment.text, comment.news, comment.author) == (
        form_data['text'], news, author
    )


def test_user_cant_use_bad_words(author_client, bad_words_data, detail_url):
    """Проверка валидации запрещенных слов в комментариях."""
    response = author_client.post(detail_url, data=bad_words_data)
    assert 'form' in response.context
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, comment, delete_url, url_to_comments
):
    """Проверка удаления комментария автором."""
    initial_data = (comment.text, comment.news, comment.author)
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0
    assert not Comment.objects.filter(
        text=initial_data[0],
        news=initial_data[1],
        author=initial_data[2]
    ).exists()


def test_user_cant_delete_comment_of_another_user(
    reader_client, comment, delete_url
):
    """Проверка запрета удаления чужого комментария."""
    initial_data = (comment.text, comment.news, comment.author)
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get(id=comment.id)
    assert (comment_from_db.text, comment_from_db.news,
            comment_from_db.author) == initial_data


def test_author_can_edit_comment(
    author_client, comment, form_data, edit_url, url_to_comments
):
    """Проверка редактирования комментария автором."""
    initial_news = comment.news
    initial_author = comment.author
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    updated_comment = Comment.objects.get(id=comment.id)
    assert (
        updated_comment.text,
        updated_comment.news,
        updated_comment.author
    ) == (
        form_data['text'], initial_news, initial_author
    )


def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, form_data, edit_url
):
    """Проверка запрета редактирования чужого комментария."""
    initial_data = (comment.text, comment.news, comment.author)
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert (comment_from_db.text, comment_from_db.news,
            comment_from_db.author) == initial_data
