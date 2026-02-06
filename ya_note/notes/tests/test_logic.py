from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .common import BaseTestCase


class TestNoteCreation(BaseTestCase):

    NOTE_TITLE = 'Новый заголовок'
    NOTE_TEXT = 'Новый текст'
    NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_user_can_create_note(self):
        notes_count_before = Note.objects.count()
        self.client.force_login(self.author)

        response = self.client.post(self.url, data=self.form_data)

        notes_count_after = Note.objects.count()
        note = Note.objects.get(slug=self.NOTE_SLUG)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(notes_count_after, notes_count_before + 1)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()

        response = self.client.post(self.url, data=self.form_data)

        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        notes_count_after = Note.objects.count()
        self.assertRedirects(response, redirect_url)
        self.assertEqual(notes_count_after, notes_count_before)

    def test_not_unique_slug(self):
        Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='existing-slug',
            author=self.author
        )
        form_data = {
            'title': 'Другой заголовок',
            'text': 'Другой текст',
            'slug': 'existing-slug'
        }
        self.client.force_login(self.author)

        response = self.client.post(self.url, data=form_data)

        notes_count = Note.objects.count()
        self.assertFormError(
            response.context['form'],
            'slug',
            f'existing-slug{WARNING}'
        )
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        form_data = {
            'title': 'Заголовок без слага',
            'text': 'Текст',
        }
        self.client.force_login(self.author)

        response = self.client.post(self.url, data=form_data)

        expected_slug = slugify(form_data['title'])
        note = Note.objects.get(slug=expected_slug)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):

    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'
    NEW_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
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

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)

        response = self.client.post(self.edit_url, data=self.form_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(
            Note.objects.get(id=self.note.id).title,
            self.NEW_TITLE
        )
        self.assertEqual(Note.objects.get(id=self.note.id).text, self.NEW_TEXT)
        self.assertEqual(Note.objects.get(id=self.note.id).slug, self.NEW_SLUG)

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.reader)

        response = self.client.post(self.edit_url, data=self.form_data)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        self.client.force_login(self.author)

        response = self.client.post(self.delete_url)

        notes_count_after = Note.objects.count()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_other_user_cant_delete_note(self):
        notes_count_before = Note.objects.count()
        self.client.force_login(self.reader)

        response = self.client.post(self.delete_url)

        notes_count_after = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count_after, notes_count_before)
