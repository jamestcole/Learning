from typing import Optional, Dict, Any, cast

from pylibraryaws.secrets_manager import SecretsManager
from pylibrarycore.datatypes.lambda_context import LambdaContext
from pylibrarycore.logging.logger_utils import setup_logging, with_lambda_logging_context, get_logger

from tooling.common.common_input_validation import CommonInputValidation
from tooling.common.error.error_response_mapper import ErrorResponseMapper
from tooling.common.git_service import GitService
from tooling.setversion.pom_update_service import PomUpdateService
from tooling.setversion.set_version_service import SetVersionService

setup_logging()
logger = get_logger(__name__)
set_version_service: Optional[SetVersionService] = None
error_response_mapper: Optional[ErrorResponseMapper] = None
common_input_validation = CommonInputValidation()


@with_lambda_logging_context
def lambda_handler(event: dict[str, str], _: LambdaContext) -> Dict[str, Any]:
    try:
        repo_name = event.get("repositoryName")
        new_pom_version = event.get("newPomVersion")
        jira_number = event.get("jiraNumber")
        branch = event.get("branchName") or "develop"

        common_input_validation.validate_repo_name(repo_name)
        common_input_validation.validate_pom_version(new_pom_version)
        common_input_validation.validate_jira_number(jira_number)
        common_input_validation.validate_branch(branch)

        _get_set_version_service().set_version(
            cast(str, repo_name),
            cast(str, new_pom_version),
            cast(str, jira_number),
            branch)
        return {
            "statusCode": 200,
            "body": f'pom(s) in {repo_name} updated to version {new_pom_version} on branch {branch or "develop"}'}
    except Exception as error:
        logger.exception("Failed to update pom(s)")
        return _get_error_response_mapper().map(error)


def _get_set_version_service() -> SetVersionService:
    global set_version_service
    set_version_service = set_version_service or SetVersionService(
        GitService(SecretsManager()),
        PomUpdateService())
    return set_version_service


def _get_error_response_mapper() -> ErrorResponseMapper:
    global error_response_mapper
    error_response_mapper = error_response_mapper or ErrorResponseMapper()
    return error_response_mapper
