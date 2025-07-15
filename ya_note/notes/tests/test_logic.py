from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты для создания заметок."""

    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст тестовой заметки'
    NOTE_SLUG = 'test-note'

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.NOTE_TITLE)
        self.assertEqual(new_note.text, self.NOTE_TEXT)
        self.assertEqual(new_note.slug, self.NOTE_SLUG)
        self.assertEqual(new_note.author, self.author)

    def test_empty_slug(self):
        """Проверка автоматической генерации slug."""
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        new_note = Note.objects.get()
        expected_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(new_note.slug, expected_slug)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Проверка, что нельзя создать заметку с уже существующим slug."""
        Note.objects.create(
            title='Первая заметка',
            text='Текст заметки',
            slug=self.NOTE_SLUG,
            author=self.author
        )
        response = self.author_client.post(self.add_url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        self.assertEqual(Note.objects.filter(slug=self.NOTE_SLUG).count(), 1)


class TestNoteEditDelete(TestCase):
    """Тесты для редактирования и удаления заметок."""

    NOTE_TITLE = 'Исходный заголовок'
    NOTE_TEXT = 'Исходный текст'
    NOTE_SLUG = 'original-note'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'
    NEW_SLUG = 'new-note'

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG
        }

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_others_note(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, self.NEW_SLUG)

    def test_user_cant_edit_others_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
