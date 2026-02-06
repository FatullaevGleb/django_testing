from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


FORM_DATA = {'text': 'Новый текст комментария'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_user_can_create_comment(author_client, author, news, detail_url):
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    comments_count_after = Comment.objects.count()
    comment = Comment.objects.latest('created')
    assertRedirects(response, f'{detail_url}#comments')
    assert comments_count_after == comments_count_before + 1
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    comments_count_after = Comment.objects.count()
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )
    assert comments_count_after == comments_count_before


def test_author_can_delete_comment(author_client, delete_url, detail_url):
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    comments_count_after = Comment.objects.count()
    assertRedirects(response, f'{detail_url}#comments')
    assert comments_count_after == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    comments_count_before = Comment.objects.count()
    response = reader_client.delete(delete_url)
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(author_client, edit_url, detail_url):
    response = author_client.post(edit_url, data=FORM_DATA)
    comment = Comment.objects.get()
    comment.refresh_from_db()
    assertRedirects(response, f'{detail_url}#comments')
    assert comment.text == FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(reader_client, edit_url):
    original_text = Comment.objects.get().text
    response = reader_client.post(edit_url, data=FORM_DATA)
    comment = Comment.objects.get()
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == original_text
