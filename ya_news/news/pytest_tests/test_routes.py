from http import HTTPStatus

import pytest
import pytest_lazyfixture
from pytest_django.asserts import assertRedirects

from .constants import HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    [
        (HOME_URL, pytest_lazyfixture.lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN_URL, pytest_lazyfixture.lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP_URL, pytest_lazyfixture.lazy_fixture('client'), HTTPStatus.OK),
    ]
)
def test_pages_availability_for_anonymous_user(
    url,
    client_fixture,
    expected_status
):
    response = client_fixture.get(url)
    assert response.status_code == expected_status


def test_logout_page_availability(client):
    response = client.post(LOGOUT_URL)
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    [
        (
            'edit_url',
            pytest_lazyfixture.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'delete_url',
            pytest_lazyfixture.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'edit_url',
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'delete_url',
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    ]
)
def test_availability_for_comment_edit_and_delete(
    request,
    url_fixture,
    client_fixture,
    expected_status
):
    url = request.getfixturevalue(url_fixture)
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    ['edit_url', 'delete_url']
)
def test_redirect_for_anonymous_client(client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
