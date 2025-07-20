from notes.forms import NoteForm

from .test_mixins import (
    BaseTestData,
    NOTE_ADD_URL,
    NOTE_EDIT_URL,
    NOTES_LIST_URL,
    NOTE_TITLE,
    NOTE_TEXT,
    NOTE_SLUG,
)


class TestNotesListForDifferentUsers(BaseTestData):
    """Тесты отображения заметок в списке для разных пользователей."""

    def test_author_sees_own_note(self):
        """Автор видит свою заметку в списке."""
        response = self.author_client.get(NOTES_LIST_URL)
        self.assertIn(self.note, response.context['object_list'])
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.slug, NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

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
