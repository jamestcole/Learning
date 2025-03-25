from unittest.mock import MagicMock
import pytest

from tooling.checkbuildstatus.lambda_function import lambda_handler
from pylibrarycore.datatypes.lambda_context import LambdaContext


@pytest.fixture()
def mock_get_build_status_service(mocker):
    return mocker.patch("tooling.checkbuildstatus.lambda_function._get_build_status_service")


def test_propagate_service_error(mock_get_build_status_service: MagicMock):
    # given
    merge_request_url = "https://gitlab.com"
    event = {
        "mergeRequestUrl": merge_request_url
    }

    error = ValueError("Failed to check build status")
    mock_get_build_status_service.return_value.fetch_build_status.side_effect = error

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

    mock_get_build_status_service.return_value.fetch_build_status.assert_called_once_with(merge_request_url)


def test_should_check_build_status(mock_get_build_status_service: MagicMock):
    # given
    merge_request_url = "https://gitlab.com"
    event = {
        "mergeRequestUrl": merge_request_url
    }
    mock_get_build_status_service.return_value.fetch_build_status.return_value = "all good"

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == "all good"
    mock_get_build_status_service.return_value.fetch_build_status.assert_called_once_with(merge_request_url)
