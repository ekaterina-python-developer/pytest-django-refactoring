from django.urls import reverse
from django.test import TestCase

from notes.forms import NoteForm


class TestNotesListForDifferentUsers(TestCase):
    """Тесты отображения заметок в списке для разных пользователей."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        cls.author = User.objects.create(username='Автор')
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = cls.client_class()
        cls.not_author_client.force_login(cls.not_author)

        from notes.models import Note
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

    def test_author_sees_own_note(self):
        """Автор видит свою заметку в списке."""
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_not_author_doesnt_see_note(self):
        """Другой пользователь не видит чужую заметку."""
        url = reverse('notes:list')
        response = self.not_author_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)


class TestPagesContainsForm(TestCase):
    """Тесты наличия формы на страницах создания и редактирования."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        cls.author = User.objects.create(username='Автор')
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        from notes.models import Note
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

    def test_add_page_contains_form(self):
        """Страница создания содержит форму."""
        url = reverse('notes:add')
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        """Страница редактирования содержит форму."""
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
