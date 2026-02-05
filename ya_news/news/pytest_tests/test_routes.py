from http import HTTPStatus

import pytest
import pytest_lazyfixture
from pytest_django.asserts import assertRedirects

from .urls import URLs

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_func, client_fixture, expected_status',
    [
        (URLs.home, pytest_lazyfixture.lazy_fixture('client'), HTTPStatus.OK),
        (URLs.login, pytest_lazyfixture.lazy_fixture('client'), HTTPStatus.OK),
        (
            URLs.signup,
            pytest_lazyfixture.lazy_fixture('client'),
            HTTPStatus.OK
        ),
    ]
)
def test_pages_availability_for_anonymous_user(
    url_func,
    client_fixture,
    expected_status
):
    response = client_fixture.get(url_func())
    assert response.status_code == expected_status


def test_logout_page_availability(client):
    response = client.post(URLs.logout())
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)


@pytest.mark.parametrize(
    'url_func, client_fixture, expected_status',
    [
        (
            URLs.edit,
            pytest_lazyfixture.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            URLs.delete,
            pytest_lazyfixture.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            URLs.edit,
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            URLs.delete,
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    ]
)
def test_availability_for_comment_edit_and_delete(
    url_func,
    client_fixture,
    comment,
    expected_status
):
    url = url_func(comment.id)
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_func',
    [URLs.edit, URLs.delete]
)
def test_redirect_for_anonymous_client(client, url_func, comment, news):
    url = url_func(comment.id)
    login_url = URLs.login()
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
