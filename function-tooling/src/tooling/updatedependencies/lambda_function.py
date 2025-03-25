from typing import Optional, cast

from pylibraryaws.secrets_manager import SecretsManager
from pylibrarycore.datatypes.lambda_context import LambdaContext
from pylibrarycore.logging.logger_utils import setup_logging, with_lambda_logging_context, get_logger

from tooling.common.common_input_validation import CommonInputValidation
from tooling.common.error.error_response_mapper import ErrorResponseMapper
from tooling.common.git_service import GitService
from tooling.updatedependencies.nexus_service import NexusService
from tooling.updatedependencies.update_project_dependencies_service import UpdateProjectDependenciesService

setup_logging()
logger = get_logger(__name__)
update_project_dependencies_service: Optional[UpdateProjectDependenciesService] = None
git_service: Optional[GitService] = None
error_response_mapper: Optional[ErrorResponseMapper] = None
common_input_validation = CommonInputValidation()


@with_lambda_logging_context
def lambda_handler(event: dict[str, str], _: LambdaContext) -> dict[str, str]:
    try:
        repo_name = event.get("repositoryName")
        jira_number = event.get("jiraNumber")
        branch = event.get("branchName") or "develop"

        common_input_validation.validate_repo_name(repo_name)
        common_input_validation.validate_jira_number(jira_number)
        common_input_validation.validate_branch(branch)

        return _get_update_project_dependencies_service().update(
            cast(str, repo_name),
            cast(str, jira_number),
            branch)
    except Exception as error:
        logger.exception("Failed to update project dependencies")
        return _get_error_response_mapper().map(error)


def _get_update_project_dependencies_service() -> UpdateProjectDependenciesService:
    global update_project_dependencies_service
    update_project_dependencies_service = update_project_dependencies_service or UpdateProjectDependenciesService(
        GitService(SecretsManager()),
        NexusService(SecretsManager()))
    return update_project_dependencies_service


def _get_error_response_mapper() -> ErrorResponseMapper:
    global error_response_mapper
    error_response_mapper = error_response_mapper or ErrorResponseMapper()
    return error_response_mapper
