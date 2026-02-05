from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from constants import HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    return News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def many_news(author):
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text=f'Текст {index}',
            date=today - timedelta(days=index)
        )
        for index in range(15)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def many_comments(author, news):
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
