from notes.forms import NoteForm

from .test_mixins import (
    BaseTestData,
    NOTE_ADD_URL,
    NOTE_EDIT_URL,
    NOTES_LIST_URL,
)


class TestNotesListForDifferentUsers(BaseTestData):
    """Тесты отображения заметок в списке для разных пользователей."""

    def test_author_sees_own_note(self):
        """Автор видит свою заметку в списке."""
        response = self.author_client.get(NOTES_LIST_URL)
        self.assertIn(self.note, response.context['object_list'])
        note_from_response = response.context['object_list'].get(
            slug=self.note.slug)
        self.assertEqual(note_from_response.title, self.note.title)
        self.assertEqual(note_from_response.text, self.note.text)
        self.assertEqual(note_from_response.slug, self.note.slug)
        self.assertEqual(note_from_response.author, self.note.author)

    def test_not_author_doesnt_see_note(self):
        """Другой пользователь не видит чужую заметку."""
        response = self.not_author_client.get(NOTES_LIST_URL)
        self.assertNotIn(self.note, response.context['object_list'])


class TestPagesContainsForm(BaseTestData):
    """Тесты наличия формы на страницах создания и редактирования."""

    def test_pages_contain_form(self):
        """Страницы создания и редактирования содержат форму."""
        urls = (
            NOTE_ADD_URL,
            NOTE_EDIT_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
