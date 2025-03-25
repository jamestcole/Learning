from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tooling.common.gitlab_service import GitLabService

SCM_PRIVATE_TOKEN = "secret-squirrel"
MERGE_REQUEST_URL = ("https://natwest.gitlab-dedicated.com/natwestgroup/DigitalX/RetailBankingDigiTech/DigitalChannels/"
                     "DigiBankingMplatform/mobile-terraform/-/merge_requests/6910")


@pytest.fixture
def mock_secrets_manager(mocker: MockerFixture):
    return mocker.patch("pylibraryaws.secrets_manager.SecretsManager")


@pytest.fixture
def mock_gitlab(mocker: MockerFixture):
    return mocker.patch("gitlab.Gitlab")


@pytest.fixture
def mock_gitlab_client(mocker: MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def mock_gitlab_project(mocker: MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def mock_gitlab_merge_request(mocker: MockerFixture):
    return mocker.MagicMock()


def test_should_get_merge_request(mock_secrets_manager: MagicMock,
                                  mock_gitlab: MagicMock,
                                  mock_gitlab_client: MagicMock,
                                  mock_gitlab_project: MagicMock,
                                  mock_gitlab_merge_request: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}

    mock_gitlab.return_value = mock_gitlab_client
    mock_gitlab_client.projects.get.return_value = mock_gitlab_project

    mock_gitlab_project.mergerequests.get.return_value = 'merge request object'
    mock_gitlab_merge_request.pipelines.list.return_value = []

    under_test = GitLabService(mock_secrets_manager.return_value)
    merge_request_url = MERGE_REQUEST_URL

    # when
    result = under_test.get_merge_request(merge_request_url)

    # then
    assert result == 'merge request object'
