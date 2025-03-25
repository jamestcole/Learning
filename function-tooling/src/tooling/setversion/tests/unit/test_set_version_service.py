from os import path

import pytest
from pytest_mock import MockerFixture

from tooling.setversion.set_version_service import SetVersionService

REPO_NAME: str = "some-repository"
NEW_POM_VERSION: str = "123.45"
LOCAL_DIR: str = "/some/local/path"
JIRA_NUMBER: str = "MPLAT-12345"
BRANCH: str = "develop"


@pytest.fixture
def mock_temporary_directory(mocker):
    return mocker.patch("tempfile.TemporaryDirectory")


@pytest.fixture
def mock_git_porcelain_service(mocker):
    return mocker.patch("tooling.common.git_service.GitService")


@pytest.fixture
def mock_pom_update_service(mocker):
    return mocker.patch("tooling.setversion.pom_update_service.PomUpdateService")


@pytest.fixture
def mock_repo(mocker: MockerFixture):
    return mocker.patch("dulwich.repo.Repo")


def test_should_checkout_update_poms_and_push(mock_temporary_directory,
                                              mock_git_porcelain_service,
                                              mock_pom_update_service,
                                              mock_repo):
    # given
    mock_git_porcelain_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    under_test = SetVersionService(mock_git_porcelain_service.return_value, mock_pom_update_service.return_value)

    # when
    under_test.set_version(REPO_NAME, NEW_POM_VERSION, JIRA_NUMBER, BRANCH)

    # then
    mock_temporary_directory.assert_called_once()
    mock_git_porcelain_service.return_value.clone_checkout.assert_called_once_with(REPO_NAME, LOCAL_DIR, BRANCH)
    mock_pom_update_service.return_value.update_pom_versions.assert_called_once_with(
        path.join(LOCAL_DIR, REPO_NAME),
        NEW_POM_VERSION)
    mock_git_porcelain_service.return_value.commit.assert_called_once_with(
        mock_repo.return_value,
        JIRA_NUMBER,
        f'updating pom version to {NEW_POM_VERSION}')
    mock_git_porcelain_service.return_value.push.assert_called_once_with(
        mock_repo.return_value,
        REPO_NAME)


def test_should_propagate_branch(mock_temporary_directory,
                                 mock_git_porcelain_service,
                                 mock_pom_update_service,
                                 mock_repo):
    # given
    mock_git_porcelain_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    under_test = SetVersionService(mock_git_porcelain_service.return_value, mock_pom_update_service.return_value)

    # when
    under_test.set_version(REPO_NAME, NEW_POM_VERSION, JIRA_NUMBER, BRANCH)

    # then
    mock_temporary_directory.assert_called_once()
    mock_git_porcelain_service.return_value.clone_checkout.assert_called_once_with(REPO_NAME, LOCAL_DIR, BRANCH)
    mock_pom_update_service.return_value.update_pom_versions.assert_called_once_with(
        path.join(LOCAL_DIR, REPO_NAME),
        NEW_POM_VERSION)
    mock_git_porcelain_service.return_value.commit.assert_called_once_with(
        mock_repo.return_value,
        JIRA_NUMBER,
        f'updating pom version to {NEW_POM_VERSION}')
    mock_git_porcelain_service.return_value.push.assert_called_once_with(
        mock_repo.return_value,
        REPO_NAME)
