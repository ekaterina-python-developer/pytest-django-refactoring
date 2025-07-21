from http import HTTPStatus


from notes.models import Note
from .test_mixins import (
    BaseTestData,
    NOTE_ADD_URL,
    NOTE_DELETE_URL,
    NOTE_EDIT_URL,
    NOTE_SUCCESS_URL,
)


class TestNoteOperations(BaseTestData):
    """Тесты для операций с заметками: создание, редактирование, удаление."""

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes = set(Note.objects.values_list('pk', flat=True))
        self.client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertEqual(notes, set(
            Note.objects.values_list('pk', flat=True)))

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(
            NOTE_ADD_URL,
            data=self.form_data
        )
        notes_after = Note.objects.exclude(id__in=notes_before)
        self.assertRedirects(response, NOTE_SUCCESS_URL)
        self.assertEqual(notes_after.count(), 1)

        new_note = notes_after.first()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Проверка, что нельзя создать заметку с уже существующим slug."""
        existing_note = Note.objects.first()
        self.form_data['slug'] = existing_note.slug
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_before, notes_after)

    def test_author_can_edit_note(self):
        """Автор может отредактировать свою заметку."""
        original_note = Note.objects.get(pk=self.note.pk)
        response = self.author_client.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertRedirects(response, NOTE_SUCCESS_URL)
        edited_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])
        self.assertEqual(edited_note.author, original_note.author)

    def test_user_cannot_edit_others_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.not_author_client.post(
            NOTE_EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(NOTE_DELETE_URL)
        self.assertRedirects(response, NOTE_SUCCESS_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
        self.assertEqual(notes_count_before - Note.objects.count(), 1)

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалить чужую заметку."""
        initial_count = Note.objects.count()
        response = self.not_author_client.delete(NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
