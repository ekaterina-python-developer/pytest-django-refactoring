import pytest
from django.conf import settings


from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, home_url):
    """Проверка количества новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, home_url):
    """Проверка сортировки новостей от новых к старым."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, detail_url, news, multiple_comments):
    """Проверка сортировки комментариев от старых к новым."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Проверка отсутствия формы комментария для анонима."""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_url):
    """Проверка наличия формы комментария для авторизованного."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_reader_sees_all_news(reader_client, home_url):
    """Проверка, что читатель видит все новости."""
    response = reader_client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE
