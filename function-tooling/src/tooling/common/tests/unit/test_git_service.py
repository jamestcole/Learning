import collections
from os import path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tooling.common.git_service import GitService
from pylibrarycore.exceptions.exceptions import InternalServerError, BadRequestException

LOCAL_DIR = "/Users/some-mplatform-user/test-git-porcelain"
REPO_NAME = "mobile-accountsummary"
SCM_PRIVATE_TOKEN = "secret-squirrel"


@pytest.fixture
def mock_secrets_manager(mocker: MockerFixture):
    return mocker.patch("pylibraryaws.secrets_manager.SecretsManager")


@pytest.fixture
def mock_clone(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.clone")


@pytest.fixture
def mock_repo(mocker: MockerFixture):
    return mocker.patch("dulwich.repo.Repo")


@pytest.fixture
def mock_checkout_branch(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.checkout_branch")


@pytest.fixture
def mock_status(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.status")


@pytest.fixture
def mock_add(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.add")


@pytest.fixture
def mock_commit(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.commit")


@pytest.fixture
def mock_active_branch(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.active_branch")


@pytest.fixture
def mock_push(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.push")


@pytest.fixture
def mock_branch_create(mocker: MockerFixture):
    return mocker.patch("dulwich.porcelain.branch_create")


@pytest.fixture
def mock_requests_post(mocker: MockerFixture):
    return mocker.patch("requests.post")


def test_should_clone_checkout(mock_secrets_manager: MagicMock,
                               mock_clone: MagicMock,
                               mock_checkout_branch: MagicMock,
                               mock_repo: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_clone.return_value = mock_repo.return_value
    under_test = GitService(mock_secrets_manager.return_value)
    expected_repo_url = ("https://natwest.gitlab-dedicated.com/natwestgroup/DigitalX/RetailBankingDigiTech/"
                         "DigitalChannels/DigiBankingMplatform/{}").format(REPO_NAME)
    branch = "branch-other-than-develop"

    # when
    repo = under_test.clone_checkout(REPO_NAME, LOCAL_DIR, branch)

    # then
    assert repo == mock_repo.return_value
    mock_secrets_manager.return_value.get_secret_value.assert_called_once_with("gitlab-tooling/1")
    mock_clone.assert_called_once_with(expected_repo_url,
                                       username="_",
                                       password=SCM_PRIVATE_TOKEN,
                                       target=path.join(LOCAL_DIR, REPO_NAME),
                                       checkout=True)
    mock_checkout_branch.assert_called_once_with(mock_repo.return_value, f'origin/{branch}')


def test_given_branch_not_specified_should_checkout_develop(mock_secrets_manager: MagicMock,
                                                            mock_clone: MagicMock,
                                                            mock_checkout_branch: MagicMock,
                                                            mock_repo: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_clone.return_value = mock_repo.return_value
    under_test = GitService(mock_secrets_manager.return_value)

    # when
    under_test.clone_checkout(REPO_NAME, LOCAL_DIR)

    # then
    mock_checkout_branch.assert_called_once_with(mock_repo.return_value, "origin/develop")


def test_should_call_get_secret_value_once(mock_secrets_manager: MagicMock,
                                           mock_clone: MagicMock,
                                           mock_checkout_branch: MagicMock,
                                           mock_repo: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_clone.return_value = mock_repo.return_value
    under_test = GitService(mock_secrets_manager.return_value)

    # when
    under_test.clone_checkout(REPO_NAME, LOCAL_DIR)
    under_test.clone_checkout(REPO_NAME, LOCAL_DIR)

    # then
    mock_secrets_manager.return_value.get_secret_value.assert_called_once_with("gitlab-tooling/1")


def test_should_add_commit(mock_secrets_manager: MagicMock,
                           mock_repo: MagicMock,
                           mock_status: MagicMock,
                           mock_add: MagicMock,
                           mock_commit: MagicMock):
    # given
    GitStatus = collections.namedtuple("GitStatus", ["unstaged"])
    unstaged_file_name = bytes("some-unstaged-file.txt", "UTF-8")
    git_status = GitStatus([unstaged_file_name])
    mock_status.return_value = git_status
    mock_repo.return_value.path = path.join(LOCAL_DIR, REPO_NAME)
    under_test = GitService(mock_secrets_manager.return_value)
    jira_number = "MPLAT-12345"

    # when
    under_test.commit(mock_repo.return_value, jira_number, "test msg")

    # then
    mock_add.assert_called_once_with(mock_repo.return_value,
                                     path.join(LOCAL_DIR, REPO_NAME, unstaged_file_name.decode("UTF-8")))
    mock_commit.assert_called_once_with(mock_repo.return_value, f'{jira_number}: test msg')


def test_should_push(mock_secrets_manager: MagicMock,
                     mock_repo: MagicMock,
                     mock_active_branch: MagicMock,
                     mock_push: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_repo.return_value.path = path.join(LOCAL_DIR, REPO_NAME)
    branch = "branch-other-than-develop"
    mock_active_branch.return_value = bytes(branch, "UTF-8")
    expected_repo_url = ("https://natwest.gitlab-dedicated.com/natwestgroup/DigitalX/RetailBankingDigiTech/"
                         "DigitalChannels/DigiBankingMplatform/{}").format(REPO_NAME)
    under_test = GitService(mock_secrets_manager.return_value)

    # when
    under_test.push(mock_repo.return_value, REPO_NAME)

    # then
    mock_push.assert_called_once_with(mock_repo.return_value,
                                      username="_",
                                      password=SCM_PRIVATE_TOKEN,
                                      remote_location=expected_repo_url,
                                      refspecs=[f'{branch}:refs/heads/{branch}'])


def test_should_create_new_branch(mock_secrets_manager: MagicMock,
                                  mock_repo: MagicMock,
                                  mock_branch_create: MagicMock,
                                  mock_checkout_branch: MagicMock):
    # given
    branch = "branch-other-than-develop"
    under_test = GitService(mock_secrets_manager.return_value)

    # when
    under_test.create_new_branch(mock_repo.return_value, branch)

    # then
    mock_branch_create.assert_called_once_with(mock_repo.return_value, branch)
    mock_checkout_branch.assert_called_once_with(mock_repo.return_value, branch)


def test_should_create_merge_request(mock_secrets_manager: MagicMock,
                                     mock_repo: MagicMock,
                                     mock_active_branch: MagicMock,
                                     mock_requests_post: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    branch = "branch-other-than-develop"
    jira_number = "MPLAT-12345"
    mock_active_branch.return_value = bytes(branch, "UTF-8")

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {'web_url': 'https://gitlab.com'}
    mock_requests_post.return_value = mock_response

    under_test = GitService(mock_secrets_manager.return_value)

    # when
    result = under_test.create_merge_request(mock_repo.return_value, REPO_NAME, branch, jira_number)

    # then
    assert result == "https://gitlab.com"


def test_should_throw_error_when_not_successful_gitlab_response(mock_secrets_manager: MagicMock,
                                                                mock_repo: MagicMock,
                                                                mock_active_branch: MagicMock,
                                                                mock_requests_post: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    branch = "branch-other-than-develop"
    jira_number = "MPLAT-12345"
    mock_active_branch.return_value = bytes(branch, "UTF-8")

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {'web_url': 'https://gitlab.com'}
    mock_requests_post.return_value = mock_response

    under_test = GitService(mock_secrets_manager.return_value)

    # when # then
    with pytest.raises(InternalServerError, match="Failed to create merge request: 500"):
        under_test.create_merge_request(mock_repo.return_value, REPO_NAME, branch, jira_number)


def test_given_unknown_branch_should_throw(mock_secrets_manager: MagicMock,
                                           mock_clone: MagicMock,
                                           mock_checkout_branch: MagicMock,
                                           mock_repo: MagicMock):
    # given
    mock_secrets_manager.return_value.get_secret_value.return_value = {"token": SCM_PRIVATE_TOKEN}
    mock_clone.return_value = mock_repo.return_value
    mock_checkout_branch.side_effect = KeyError("Are you the keymaster?")
    under_test = GitService(mock_secrets_manager.return_value)

    # when/then
    with pytest.raises(BadRequestException, match="Unable to checkout develop"):
        under_test.clone_checkout(REPO_NAME, LOCAL_DIR)
