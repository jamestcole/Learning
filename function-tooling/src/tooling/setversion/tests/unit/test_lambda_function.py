from unittest.mock import MagicMock

import pytest
from pylibrarycore.datatypes.lambda_context import LambdaContext  # type: ignore

from tooling.setversion.lambda_function import lambda_handler


@pytest.fixture()
def mock_get_set_version_service(mocker):
    return mocker.patch("tooling.setversion.lambda_function._get_set_version_service")


@pytest.fixture()
def mock_error_response_mapper(mocker):
    return mocker.patch("tooling.setversion.lambda_function._get_error_response_mapper")


def test_throw_error_invalid_repo_name():
    # given
    repository_name = "!!@@"
    jira_number = "MPLAT-12345"
    branch = "not-develop"
    new_pom_version = "123.45"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch,
        "newPomVersion": new_pom_version,
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        'body': {
            'errorCode': 400,
            'errorMessage': 'Please supply a valid repo_name matching the pattern: ^[\\w_-]+$'
        },
        'statusCode': 400
    }


def test_throw_error_invalid_jira_number():
    # given
    repository_name = "mobile-token"
    jira_number = "!!@@"
    branch = "not-develop"
    new_pom_version = "123.45"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch,
        "newPomVersion": new_pom_version,
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        'body': {
            'errorCode': 400,
            'errorMessage': 'Please supply a valid jira_number matching the pattern: ^MPLAT-\\d{4,}$'
        },
        'statusCode': 400
    }


def test_throw_error_invalid_branch():
    # given
    repository_name = "mobile-token"
    jira_number = "MPLAT-12345"
    branch = "!!@@"
    new_pom_version = "123.45"
    event = {
        "repositoryName": repository_name,
        "jiraNumber": jira_number,
        "branchName": branch,
        "newPomVersion": new_pom_version,
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        'body': {
            'errorCode': 400,
            'errorMessage': 'Please supply a valid branch matching the pattern: ^[/\\w_-]+$'
        },
        'statusCode': 400
    }


def test_throw_error_invalid_pom_version():
    # given
    repository_name = "mobile-somerepository"
    new_pom_version = "%$#"
    jira_number = "MPLAT-12345"
    event = {
        "repositoryName": repository_name,
        "newPomVersion": new_pom_version,
        "jiraNumber": jira_number
    }

    # when
    result = lambda_handler(event, LambdaContext())

    # then
    assert result == {
        'body': {
            'errorCode': 400,
            'errorMessage': 'Unable to parse %$# as a maven version'
        },
        'statusCode': 400
    }


def test_can_handle(mock_get_set_version_service: MagicMock):
    # given
    repository_name = "mobile-somerepository"
    new_pom_version = "123.45"
    jira_number = "MPLAT-12345"
    event = {
        "repositoryName": repository_name,
        "newPomVersion": new_pom_version,
        "jiraNumber": jira_number
    }

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == {
        "statusCode": 200,
        "body": f'pom(s) in {repository_name} updated to version {new_pom_version} on branch develop'
    }
    mock_get_set_version_service.return_value.set_version.assert_called_once_with(
        repository_name,
        new_pom_version,
        jira_number,
        'develop')


def test_given_branch_supplied_can_handle(mock_get_set_version_service: MagicMock):
    # given
    repository_name = "mobile-somerepository"
    new_pom_version = "123.45"
    jira_number = "MPLAT-12345"
    branch = "not-develop"
    event = {
        "repositoryName": repository_name,
        "newPomVersion": new_pom_version,
        "jiraNumber": jira_number,
        "branchName": branch
    }

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == {
        "statusCode": 200,
        "body": f'pom(s) in {repository_name} updated to version {new_pom_version} on branch {branch}'
    }
    mock_get_set_version_service.return_value.set_version.assert_called_once_with(repository_name,
                                                                                  new_pom_version,
                                                                                  jira_number,
                                                                                  branch)


def test_given_upstream_error_should_map(mock_get_set_version_service: MagicMock,
                                         mock_error_response_mapper: MagicMock):
    # given
    repository_name = "mobile-somerepository"
    pom_version = "3.0.0-SNAPSHOT"
    jira_number = "MPLAT-12345"
    branch = "not-develop"
    event = {
        "repositoryName": repository_name,
        "newPomVersion": pom_version,
        "jiraNumber": jira_number,
        "branchName": branch
    }
    error = ValueError("Some error")
    mock_get_set_version_service.return_value.set_version.side_effect = error
    error_response_mapper_response = {
        "statusCode": 500,
        "body": {
            "errorCode": 500,
            "errorMessage": "Not handled error"
        }
    }
    mock_error_response_mapper.return_value.map.return_value = error_response_mapper_response

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == error_response_mapper_response
    mock_get_set_version_service.return_value.set_version.assert_called_once_with(
        repository_name,
        pom_version,
        jira_number,
        branch)
    mock_error_response_mapper.return_value.map.assert_called_once_with(error)
