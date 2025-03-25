import re

from packaging import version
from pylibrarycore.exceptions.exceptions import BadRequestException


class CommonInputValidation:
    __branch_pattern = r'^[/\w_-]+$'
    __repository_pattern = r'^[\w_-]+$'
    __jira_number_pattern = r'^MPLAT-\d{4,}$'

    @staticmethod
    def validate_repo_name(repo_name: str | None) -> None:
        if not (repo_name and re.match(CommonInputValidation.__branch_pattern, repo_name)):
            raise BadRequestException(
                "Please supply a valid repo_name matching the pattern: "
                f'{CommonInputValidation.__repository_pattern}')

    @staticmethod
    def validate_jira_number(jira_number: str | None) -> None:
        if not (jira_number and re.match(CommonInputValidation.__jira_number_pattern, jira_number)):
            raise BadRequestException(
                "Please supply a valid jira_number matching the pattern: "
                f'{CommonInputValidation.__jira_number_pattern}')

    @staticmethod
    def validate_branch(branch: str | None) -> None:
        if not (branch and re.match(CommonInputValidation.__branch_pattern, branch)):
            raise BadRequestException(
                "Please supply a valid branch matching the pattern: "
                f'{CommonInputValidation.__branch_pattern}')

    @staticmethod
    def validate_pom_version(pom_version: str | None) -> None:
        try:
            if not pom_version:
                raise ValueError("falsy pom_version")
            version.parse(pom_version.removesuffix("-SNAPSHOT"))
        except Exception:
            raise BadRequestException(f'Unable to parse {pom_version} as a maven version')
