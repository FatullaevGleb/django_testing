from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    return User.objects.create(username='Автор комментария')


@pytest.fixture
def reader():
    return User.objects.create(username='Читатель')


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
def news():
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
def many_news():
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
