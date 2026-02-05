from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

from .common import BaseTestCase


class TestListPage(BaseTestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок автора',
            text='Текст заметки автора',
            slug='author-note',
            author=cls.author
        )
        Note.objects.create(
            title='Заголовок читателя',
            text='Текст заметки читателя',
            slug='reader-note',
            author=cls.reader
        )

    def test_notes_list_for_author(self):
        # Arrange
        self.client.force_login(self.author)

        # Act
        response = self.client.get(self.LIST_URL)

        # Assert
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)

    def test_notes_list_for_reader(self):
        # Arrange
        self.client.force_login(self.reader)

        # Act
        response = self.client.get(self.LIST_URL)

        # Assert
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)


class TestDetailPage(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        # Arrange
        self.client.force_login(self.author)

        # Act
        url = reverse('notes:list')
        response = self.client.get(url)

        # Assert
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)


class TestFormPages(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_add_page_contains_form(self):
        # Arrange
        self.client.force_login(self.author)

        # Act
        url = reverse('notes:add')
        response = self.client.get(url)

        # Assert
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        # Arrange
        self.client.force_login(self.author)

        # Act
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)

        # Assert
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
