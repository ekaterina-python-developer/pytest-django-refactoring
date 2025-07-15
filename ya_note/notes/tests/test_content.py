from http import HTTPStatus
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
    """Тесты страницы со списком заметок."""

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создаем тестовые данные."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        today = timezone.now()
        all_notes = (
            Note(
                title=f'Заголовок {index}',
                text='Текст заметки',
                slug=f'test-slug-{index}',
                author=cls.author,
                date=today - timedelta(days=index))
            for index in range(settings.NOTE_COUNT_ON_HOME_PAGE + 1)
        )
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        """Проверяем ограничение количества заметок на странице."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, settings.NOTE_COUNT_ON_HOME_PAGE)

    def test_notes_order(self):
        """Проверяем сортировку заметок (новые сначала)."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_dates = [notes.date for notes in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestNoteCreateForm(TestCase):
    """Тесты формы создания заметки."""

    @classmethod
    def setUpTestData(cls):
        """Подготавливаем тестовые данные."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.detail_url = reverse('notes:add')

    def test_authorized_client_has_form(self):
        """Проверяем наличие формы у авторизованного пользователя."""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_client_has_no_form(self):
        """Проверяем редирект анонимного пользователя на страницу входа."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse('users:login'), response.url)


class TestNoteUpdateForm(TestCase):
    """Тесты формы редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        """Подготавливаем тестовые данные."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )
        cls.update_url = reverse('notes:edit', kwargs={'slug': cls.note.slug})

    def test_authorized_author_has_form(self):
        """Проверяем доступ автора к форме редактирования."""
        self.client.force_login(self.author)
        response = self.client.get(self.update_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
        self.assertEqual(response.context['form'].instance.pk, self.note.pk)


class TestNoteDetailView(TestCase):
    """Тесты страницы просмотра заметки."""

    @classmethod
    def setUpTestData(cls):
        """Подготавливаем тестовые данные."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Содержание заметки',
            slug='test-note',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', kwargs={
                                 'slug': cls.note.slug})

    def test_authorized_author_can_view_note(self):
        """Проверяем доступ автора к своей заметке."""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('note', response.context)
        self.assertEqual(response.context['note'].pk, self.note.pk)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_anonymous_user_redirected_to_login(self):
        """Проверяем редирект анонимного пользователя на страницу входа."""
        login_url = reverse('users:login')
        response = self.client.get(self.detail_url)
        expected_url = f"{login_url}?next={self.detail_url}"
        self.assertRedirects(response, expected_url)
