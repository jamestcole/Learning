from typing import Optional, Any

from pylibraryaws.secrets_manager import SecretsManager
from pylibrarycore.datatypes.lambda_context import LambdaContext
from pylibrarycore.logging.logger_utils import setup_logging, with_lambda_logging_context, get_logger

from tooling.common.gitlab_service import GitLabService
from tooling.common.error.error_response_mapper import ErrorResponseMapper

setup_logging()
logger = get_logger(__name__)
gitlab_service: Optional[GitLabService] = None
error_response_mapper: Optional[ErrorResponseMapper] = None


@with_lambda_logging_context
def lambda_handler(event: dict[str, str], _: LambdaContext) -> dict[str, Any]:
    try:
        merge_request_url = event["mergeRequestUrl"]
        merge_request = _get_gitlab_service().get_merge_request(merge_request_url)
        merge_request.approve()
        merge_request.merge()
        return {
            "statusCode": 200,
            "body": "build has been approved and merged"
        }
    except Exception as error:
        logger.exception("Failed to approve and merge the build")
        return _get_error_response_mapper().map(error)


def _get_gitlab_service() -> GitLabService:
    global gitlab_service
    gitlab_service = gitlab_service or GitLabService(SecretsManager())
    return gitlab_service


def _get_error_response_mapper() -> ErrorResponseMapper:
    global error_response_mapper
    error_response_mapper = error_response_mapper or ErrorResponseMapper()
    return error_response_mapper
