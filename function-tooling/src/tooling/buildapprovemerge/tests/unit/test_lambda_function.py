from unittest.mock import MagicMock
import pytest

from tooling.buildapprovemerge.lambda_function import lambda_handler
from pylibrarycore.datatypes.lambda_context import LambdaContext


@pytest.fixture()
def gitlab_service(mocker):
    return mocker.patch("tooling.buildapprovemerge.lambda_function._get_gitlab_service")


@pytest.fixture()
def merge_request(mocker):
    return mocker.MagicMock()


def test_propagate_service_error(gitlab_service: MagicMock):
    # given
    merge_request_url = "https://gitlab.com"
    event = {
        "mergeRequestUrl": merge_request_url
    }

    error = ValueError("Failed to approve and merge the build")
    gitlab_service.return_value.get_merge_request.side_effect = error

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

    gitlab_service.return_value.get_merge_request.assert_called_once_with(merge_request_url)


def test_should_approve_and_merge(gitlab_service: MagicMock,
                                  merge_request: MagicMock):
    # given
    merge_request_url = "https://gitlab.com"
    event = {
        "mergeRequestUrl": merge_request_url
    }
    gitlab_service.return_value.get_merge_request.return_value = merge_request

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == {
        "statusCode": 200,
        "body": "build has been approved and merged"
    }
    gitlab_service.return_value.get_merge_request.assert_called_once_with(merge_request_url)
    merge_request.approve.assert_called_once()
    merge_request.merge.assert_called_once()
