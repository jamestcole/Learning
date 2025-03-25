from pylibrarycore.datatypes.lambda_context import LambdaContext  # type: ignore

from tooling.generateserviceversionspage.lambda_function import lambda_handler


def test_can_handle():
    # given
    event = {
        "requestContext": {
            "extendedRequestId": "some-request-id"
        }
    }

    # when
    response = lambda_handler(event, LambdaContext())

    # then
    assert response == {"generate": "service versions page"}
