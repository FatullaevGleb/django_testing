from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .urls import URLs

pytestmark = pytest.mark.django_db


FORM_DATA = {'text': 'Новый текст комментария'}


def test_anonymous_user_cant_create_comment(client, news):
    comments_count_before = Comment.objects.count()
    client.post(URLs.detail(news.id), data=FORM_DATA)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_user_can_create_comment(author_client, author, news):
    comments_count_before = Comment.objects.count()
    response = author_client.post(URLs.detail(news.id), data=FORM_DATA)
    comments_count_after = Comment.objects.count()
    comment = Comment.objects.latest('created')
    assertRedirects(response, f'{URLs.detail(news.id)}#comments')
    assert comments_count_after == comments_count_before + 1
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    comments_count_before = Comment.objects.count()
    response = author_client.post(URLs.detail(news.id), data=bad_words_data)
    comments_count_after = Comment.objects.count()
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )
    assert comments_count_after == comments_count_before


def test_author_can_delete_comment(author_client, comment, news):
    comments_count_before = Comment.objects.count()
    response = author_client.delete(URLs.delete(comment.id))
    comments_count_after = Comment.objects.count()
    assertRedirects(response, f'{URLs.detail(news.id)}#comments')
    assert comments_count_after == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    comments_count_before = Comment.objects.count()
    response = reader_client.delete(URLs.delete(comment.id))
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(author_client, comment, news):
    response = author_client.post(URLs.edit(comment.id), data=FORM_DATA)
    comment.refresh_from_db()
    assertRedirects(response, f'{URLs.detail(news.id)}#comments')
    assert comment.text == FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    response = reader_client.post(URLs.edit(comment.id), data=FORM_DATA)
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != FORM_DATA['text']
