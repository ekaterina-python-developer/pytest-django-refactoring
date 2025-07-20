from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

# Константы для тестовых данных
NOTE_TITLE = 'Тестовая заметка'
NOTE_TEXT = 'Текст заметки'
NOTE_SLUG = 'test-note'
NEW_NOTE_TITLE = 'Новый заголовок'
NEW_NOTE_TEXT = 'Новый текст'
NEW_NOTE_SLUG = 'new-note'

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

# Константы из настроек приложения
NOTE_COUNT_ON_HOME_PAGE = settings.NOTE_COUNT_ON_HOME_PAGE


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

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )

        cls.NOTE_EDIT_URL = reverse('notes:edit', args=[cls.note.slug])
        cls.NOTE_DETAIL_URL = reverse('notes:detail', args=[cls.note.slug])
        cls.NOTE_DELETE_URL = reverse('notes:delete', args=[cls.note.slug])

        cls.REDIRECT_AFTER_LOGIN = {
            'edit': f'{LOGIN_URL}?next={cls.NOTE_EDIT_URL}',
            'delete': f'{LOGIN_URL}?next={cls.NOTE_DELETE_URL}',
        }

        cls.form_data = {
            'title': NEW_NOTE_TITLE,
            'text': NEW_NOTE_TEXT,
            'slug': NEW_NOTE_SLUG
        }

        cls.duplicate_data = {
            'title': 'Дубликат заметки',
            'text': 'Текст дубликата заметки',
            'slug': NOTE_SLUG
        }
