import re

import pytest
from pylibrarycore.exceptions.exceptions import BadRequestException

from tooling.common.common_input_validation import CommonInputValidation

REPO_NAME: str = "some-repository"
LOCAL_DIR: str = "/some/local/path"
JIRA_NUMBER: str = "MPLAT-12345"
NS_MAP = {"": "http://maven.apache.org/POM/4.0.0"}


def test_should_allow_mixed_case_number_dash_and_underscores_in_repo_name():
    # given
    under_test = CommonInputValidation()

    # when # then
    try:
        under_test.validate_repo_name("Some-Repository_new_123")
    except BadRequestException as e:
        pytest.fail(f"Unexpected error: {e}")


def test_given_invalid_repo_name_should_throw():
    # given
    pattern = re.escape(r'^[\w_-]+$')
    under_test = CommonInputValidation()

    # when # then
    with pytest.raises(BadRequestException, match=f'Please supply a valid repo_name matching the pattern: {pattern}'):
        under_test.validate_repo_name("____123!")


def test_should_allow_mixed_case_number_dash_and_underscores_in_branch():
    # given
    under_test = CommonInputValidation()

    # when # then
    try:
        under_test.validate_branch("Some-branch_456")
    except BadRequestException as e:
        pytest.fail(f"Unexpected error: {e}")


def test_given_invalid_branch_should_throw():
    # given
    pattern = re.escape(r'^[/\w_-]+$')
    under_test = CommonInputValidation()

    # when # then
    with pytest.raises(BadRequestException, match=f'Please supply a valid branch matching the pattern: {pattern}'):
        under_test.validate_branch("!^&%$")


def test_should_allow_valid_jira_number():
    # given
    under_test = CommonInputValidation()

    # when # then
    try:
        under_test.validate_jira_number("MPLAT-12345")
    except BadRequestException as e:
        pytest.fail(f"Unexpected error: {e}")


def test_given_invalid_jira_number_should_throw():
    # given
    pattern = re.escape(r'^MPLAT-\d{4,}$')
    under_test = CommonInputValidation()

    # when # then
    with pytest.raises(BadRequestException, match=f'Please supply a valid jira_number matching the pattern: {pattern}'):
        under_test.validate_jira_number("AVIATO-12345")


def test_should_allow_valid_pom_version():
    # given
    under_test = CommonInputValidation()

    # when # then
    try:
        under_test.validate_pom_version("5.1.0-SNAPSHOT")
    except BadRequestException as e:
        pytest.fail(f"Unexpected error: {e}")


def test_given_invalid_pom_version_should_throw():
    # given
    invalid_version = "123.45-USE_THIS_ONE_NEW_FINAL_2"
    under_test = CommonInputValidation()

    # when # then
    with pytest.raises(BadRequestException, match=f'Unable to parse {invalid_version} as a maven version'):
        under_test.validate_pom_version(invalid_version)


def test_given_none_pom_version_should_throw():
    # given
    under_test = CommonInputValidation()

    # when # then
    with pytest.raises(BadRequestException, match="Unable to parse None as a maven version"):
        under_test.validate_pom_version(None)
