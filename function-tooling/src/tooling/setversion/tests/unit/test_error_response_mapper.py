from typing import Any

from pylibrarycore.exceptions.exceptions import BadRequestException

from tooling.common.error.error_response_mapper import ErrorResponseMapper

under_test: ErrorResponseMapper = ErrorResponseMapper()


def test_should_map_bad_request_exception():
    # given
    message: str = "You requested...poorly"
    response_code = 400
    e: BadRequestException = BadRequestException(message)

    # when
    response: dict[str, Any] = under_test.map(e)

    # then
    assert list(response.keys()) == ["statusCode", "body"]
    assert response["statusCode"] == response_code
    body: dict[str, str] = response["body"]
    assert list(body.keys()) == ["errorCode", "errorMessage"]
    assert body["errorCode"] == response_code
    assert body["errorMessage"] == message


def test_should_map_non_standard_exception():
    message = "some-non-base-lambda-exception"
    response_code = 500
    e: ValueError = ValueError(message)

    # when
    response: dict[str, Any] = under_test.map(e)

    # then
    assert list(response.keys()) == ["statusCode", "body"]
    assert response["statusCode"] == response_code
    body: dict[str, str] = response["body"]
    assert list(body.keys()) == ["errorCode", "errorMessage"]
    assert body["errorCode"] == response_code
    assert body["errorMessage"] == "Not handled error"
