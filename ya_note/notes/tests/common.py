from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для всех тестов с общими данными."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
