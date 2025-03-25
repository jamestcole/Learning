from unittest.mock import MagicMock
import pytest

from tooling.updatedependencies.nexus_service import NexusService
from unittest.mock import Mock
from pytest_mock import MockerFixture
from pylibrarycore.exceptions.exceptions import InternalServerError

NEXUS_USERNAME = "nexus-secret-username"
NEXUS_PASSWORD = "nexus-secret-password"


@pytest.fixture
def mock_secrets_manager(mocker: MockerFixture):
    return mocker.patch("pylibraryaws.secrets_manager.SecretsManager")


@pytest.fixture
def mock_requests_get(mocker: MockerFixture):
    return mocker.patch("requests.get")


def test_nexus_error_response(mock_secrets_manager: MagicMock,
                              mock_requests_get: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {
        "username": NEXUS_USERNAME,
        "password": NEXUS_PASSWORD
    }

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "failed"}

    mock_requests_get.return_value = mock_response
    under_test = NexusService(mock_secrets_manager.return_value)

    # when
    with pytest.raises(InternalServerError, match="Failed to call Nexus. Status code: 500 "
                                                  "and body: {'error': 'failed'}"):
        under_test.fetch_latest_version('some-artifact-id')


def test_no_releases_found(mock_secrets_manager: MagicMock,
                           mock_requests_get: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {
        "username": NEXUS_USERNAME,
        "password": NEXUS_PASSWORD
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}

    mock_requests_get.return_value = mock_response
    under_test = NexusService(mock_secrets_manager.return_value)

    # when
    with pytest.raises(InternalServerError, match="No version has been found for artifact id: \\[some-artifact-id]"):
        under_test.fetch_latest_version('some-artifact-id')


def test_fetch_latest_version(mock_secrets_manager: MagicMock,
                              mock_requests_get: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {
        "username": NEXUS_USERNAME,
        "password": NEXUS_PASSWORD
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "version": "100"
            }
        ]
    }

    mock_requests_get.return_value = mock_response
    under_test = NexusService(mock_secrets_manager.return_value)

    # when
    result = under_test.fetch_latest_version('some-artifact-id')

    # then
    assert result == '100'
