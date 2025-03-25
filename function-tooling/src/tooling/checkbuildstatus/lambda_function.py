from typing import Optional

from pylibraryaws.secrets_manager import SecretsManager
from pylibrarycore.datatypes.lambda_context import LambdaContext
from pylibrarycore.logging.logger_utils import setup_logging, with_lambda_logging_context, get_logger

from tooling.common.gitlab_service import GitLabService
from tooling.checkbuildstatus.build_status_service import BuildStatusService
from tooling.common.error.error_response_mapper import ErrorResponseMapper

setup_logging()
logger = get_logger(__name__)
build_status_service: Optional[BuildStatusService] = None
error_response_mapper: Optional[ErrorResponseMapper] = None


@with_lambda_logging_context
def lambda_handler(event: dict[str, str], _: LambdaContext) -> dict[str, str]:
    try:
        merge_request_url = event["mergeRequestUrl"]
        return _get_build_status_service().fetch_build_status(merge_request_url)
    except Exception as error:
        logger.exception("Failed to check build status")
        return _get_error_response_mapper().map(error)


def _get_build_status_service() -> BuildStatusService:
    global build_status_service
    secrets_manager = SecretsManager()
    build_status_service = build_status_service or BuildStatusService(secrets_manager, GitLabService(secrets_manager))
    return build_status_service


def _get_error_response_mapper() -> ErrorResponseMapper:
    global error_response_mapper
    error_response_mapper = error_response_mapper or ErrorResponseMapper()
    return error_response_mapper
