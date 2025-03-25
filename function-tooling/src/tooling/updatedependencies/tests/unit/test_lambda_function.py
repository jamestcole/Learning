from unittest.mock import MagicMock
import pytest

from tooling.updatedependencies.lambda_function import lambda_handler
from pylibrarycore.datatypes.lambda_context import LambdaContext


@pytest.fixture()
def mock_get_update_project_dependencies_service(mocker):
    return mocker.patch("tooling.updatedependencies.lambda_function._get_update_project_dependencies_service")


def test_throw_error_invalid_repo_name():
    # given
    repository_name = "!!@@"
    jira_number = "MPLAT-12345"
    branch = "not-develop"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        "body": {
            "errorCode": 400,
            "errorMessage": 'Please supply a valid repo_name matching the pattern: ^[\\w_-]+$'
        },
        "statusCode": 400
    }


def test_throw_error_invalid_jira_number():
    # given
    repository_name = "mobile-token"
    jira_number = "!!@@"
    branch = "not-develop"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        "body": {
            "errorCode": 400,
            "errorMessage": 'Please supply a valid jira_number matching the pattern: ^MPLAT-\\d{4,}$'
        },
        "statusCode": 400
    }


def test_throw_error_invalid_branch():
    # given
    repository_name = "mobile-token"
    jira_number = "MPLAT-12345"
    branch = "!!@@"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        "body": {
            "errorCode": 400,
            "errorMessage": 'Please supply a valid branch matching the pattern: ^[/\\w_-]+$'
        },
        "statusCode": 400
    }


def test_propagate_service_error(mock_get_update_project_dependencies_service: MagicMock):
    # given
    repository_name = "mobile-token"
    jira_number = "MPLAT-12345"
    branch = "non-develop"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch
    }

    error = ValueError("Failed to update project dependencies")
    mock_get_update_project_dependencies_service.return_value.update.side_effect = error

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        "body": {
            "errorCode": 500,
            "errorMessage": "Not handled error"
        },
        "statusCode": 500
    }

    mock_get_update_project_dependencies_service.return_value.update.assert_called_once_with(repository_name,
                                                                                             jira_number,
                                                                                             branch)


def test_should_update_dependencies_with_branch_supplied(mock_get_update_project_dependencies_service: MagicMock):
    # given
    repository_name = "mobile-token"
    jira_number = "MPLAT-12345"
    branch = "non-develop"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch
    }
    mock_get_update_project_dependencies_service.return_value.update.return_value = "all good"

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == "all good"
    mock_get_update_project_dependencies_service.return_value.update.assert_called_once_with(
        repository_name,
        jira_number,
        branch)


def test_should_update_dependencies_with_no_branch_supplied(mock_get_update_project_dependencies_service: MagicMock):
    # given
    repository_name = "mobile-token"
    jira_number = "MPLAT-12345"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number
    }
    mock_get_update_project_dependencies_service.return_value.update.return_value = "all good"

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == "all good"
    mock_get_update_project_dependencies_service.return_value.update.assert_called_once_with(
        repository_name,
        jira_number,
        "develop")
