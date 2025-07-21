from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

# Константы для тестовых данных
NOTE_SLUG = 'test-note'

# Константы для URL
NOTES_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
NOTE_EDIT_URL = reverse('notes:edit', args=[NOTE_SLUG])
NOTE_DETAIL_URL = reverse('notes:detail', args=[NOTE_SLUG])
HOME_URL = reverse('notes:home')
NOTE_SUCCESS_URL = reverse('notes:success')
NOTE_DELETE_URL = reverse('notes:delete', args=[NOTE_SLUG])
LOGIN_URL = reverse('users:login')
LOGIN_REDIRECT_URL = reverse('notes:home')

NOTE_EDIT_URL = reverse('notes:edit', args=[NOTE_SLUG])
NOTE_DELETE_URL = reverse('notes:delete', args=[NOTE_SLUG])

REDIRECT_AFTER_LOGIN = {
    'edit': f'{LOGIN_URL}?next={NOTE_EDIT_URL}',
    'delete': f'{LOGIN_URL}?next={NOTE_DELETE_URL}',
}


class BaseTestData(TestCase):
    """Базовый класс для тестовых данных."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'new-note'
        }
