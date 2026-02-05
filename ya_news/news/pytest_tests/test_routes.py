from http import HTTPStatus

import pytest
import pytest_lazyfixture
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_home_availability_for_anonymous_user(client, home_url):
    # Arrange
    # (данные подготовлены фикстурами)

    # Act
    response = client.get(home_url)

    # Assert
    assert response.status_code == HTTPStatus.OK


def test_detail_availability_for_anonymous_user(client, detail_url):
    # Arrange
    # (данные подготовлены фикстурами)

    # Act
    response = client.get(detail_url)

    # Assert
    assert response.status_code == HTTPStatus.OK


def test_login_page_availability(client, login_url):
    # Arrange
    # (данные подготовлены фикстурами)

    # Act
    response = client.get(login_url)

    # Assert
    assert response.status_code == HTTPStatus.OK


def test_signup_page_availability(client, signup_url):
    # Arrange
    # (данные подготовлены фикстурами)

    # Act
    response = client.get(signup_url)

    # Assert
    assert response.status_code == HTTPStatus.OK


def test_logout_page_availability(client, logout_url):
    # Arrange
    # (данные подготовлены фикстурами)

    # Act
    response = client.post(logout_url)

    # Assert
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (
            pytest_lazyfixture.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    ],
)
@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_availability_for_comment_edit_and_delete(
    parametrized_client, url_name, comment, expected_status
):
    # Arrange
    url = reverse(url_name, args=(comment.id,))

    # Act
    response = parametrized_client.get(url)

    # Assert
    assert response.status_code == expected_status


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_redirect_for_anonymous_client(
    client, url_name, comment, login_url
):
    # Arrange
    url = reverse(url_name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'

    # Act
    response = client.get(url)

    # Assert
    assertRedirects(response, expected_url)
