from http import HTTPStatus

from django.urls import reverse

from notes.models import Note

from .common import BaseTestCase


class TestRoutes(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_pages_availability_for_anonymous_user(self):
        # Arrange
        urls = [
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        ]

        # Act & Assert
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_page_availability(self):
        # Arrange
        url = reverse('users:logout')

        # Act
        response = self.client.post(url)

        # Assert
        self.assertIn(response.status_code, (HTTPStatus.OK, HTTPStatus.FOUND))

    def test_pages_availability_for_auth_user(self):
        # Arrange
        self.client.force_login(self.reader)
        urls = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        ]

        # Act & Assert
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        # Arrange
        users_statuses = [
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        ]

        # Act & Assert
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(
                    user=user.username,
                    name=name,
                    status=status
                ):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Arrange
        login_url = reverse('users:login')
        urls = [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ]

        # Act & Assert
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
