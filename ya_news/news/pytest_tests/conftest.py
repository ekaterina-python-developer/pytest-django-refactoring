from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def news_batch():
    """Создание тестовых новостей для главной страницы."""
    News.objects.bulk_create(
        News(title=f'Новость {index}', text='Просто текст.',
             date=datetime.today() - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def news():
    """Создает тестовую новость."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(django_user_model):
    """Пользователь-автор."""
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def author_client(author):
    """Авторизованный клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    """Пользователь-читатель."""
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def reader_client(reader):
    """Авторизованный клиент читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(author, news):
    """Тестовый комментарий."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def multiple_comments(news, author):
    """Несколько комментариев с разными датами."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}')
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_comments(detail_url):
    """URL с якорем к комментариям."""
    return f'{detail_url}#comments'


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def edit_redirect_url(edit_url, login_url):
    """URL для редиректа с edit_url."""
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def delete_redirect_url(delete_url, login_url):
    """URL для редиректа с delete_url."""
    return f'{login_url}?next={delete_url}'
