import pytest

from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, home_url):
    """Проверка количества новостей на главной странице."""
    response = client.get(home_url)
    news = response.context['object_list']
    assert news.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url):
    """Проверка сортировки новостей от новых к старым."""
    response = client.get(home_url)
    news = response.context['object_list']
    all_dates = [news_item.date for news_item in news]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, detail_url, news, multiple_comments):
    """Проверка сортировки комментариев от старых к новым."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    assert list(news.comment_set.values_list('created', flat=True)) == sorted(
        news.comment_set.values_list('created', flat=True)
    )


def test_anonymous_client_has_no_form(client, detail_url):
    """Проверка отсутствия формы комментария для анонима."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Проверка наличия формы комментария для авторизованного."""
    response = author_client.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm)
