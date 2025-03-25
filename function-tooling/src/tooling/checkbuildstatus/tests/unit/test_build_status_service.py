from unittest.mock import MagicMock
import pytest

from tooling.checkbuildstatus.build_status_service import BuildStatusService
from pytest_mock import MockerFixture

SCM_PRIVATE_TOKEN = "secret-squirrel"


@pytest.fixture
def mock_secrets_manager(mocker: MockerFixture):
    return mocker.patch("pylibraryaws.secrets_manager.SecretsManager")


@pytest.fixture
def mock_gitlab_service(mocker: MockerFixture):
    return mocker.patch("tooling.common.gitlab_service.GitLabService")


@pytest.fixture
def mock_gitlab_merge_request(mocker: MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def mock_gitlab_pipeline(mocker: MockerFixture):
    return mocker.MagicMock()


def test_should_return_not_started_when_no_pipelines(mock_secrets_manager: MagicMock,
                                                     mock_gitlab_service: MagicMock,
                                                     mock_gitlab_merge_request: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_gitlab_service.return_value.get_merge_request.return_value = mock_gitlab_merge_request
    mock_gitlab_merge_request.pipelines.list.return_value = []

    under_test = BuildStatusService(mock_secrets_manager.return_value, mock_gitlab_service.return_value)

    # when
    result = under_test.fetch_build_status("url")

    # then
    assert result == {
        "statusCode": 200,
        "body": "build has not started yet"
    }


@pytest.mark.parametrize(
    "build_status",
    [
        'running',
        'pending',
        'success'
    ]
)
def test_should_return_running_pipeline(mock_secrets_manager: MagicMock,
                                        mock_gitlab_service: MagicMock,
                                        mock_gitlab_merge_request: MagicMock,
                                        mock_gitlab_pipeline: MagicMock,
                                        build_status: str):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_gitlab_service.return_value.get_merge_request.return_value = mock_gitlab_merge_request
    mock_gitlab_merge_request.pipelines.list.return_value = [mock_gitlab_pipeline]
    mock_gitlab_pipeline.status = build_status

    under_test = BuildStatusService(mock_secrets_manager.return_value, mock_gitlab_service.return_value)

    # when
    result = under_test.fetch_build_status("url")

    # then
    assert result == {
        "statusCode": 200,
        "body": build_status
    }
