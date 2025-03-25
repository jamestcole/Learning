import pytest
import xml.etree.ElementTree as ET  # nosec

from tooling.updatedependencies.update_project_dependencies_service import UpdateProjectDependenciesService
from pytest_mock import MockerFixture
from pyfakefs.fake_filesystem import FakeFilesystem
from pylibrarycore.exceptions.exceptions import InternalServerError

REPO_NAME: str = "some-repository"
LOCAL_DIR: str = "/some/local/path"
JIRA_NUMBER: str = "MPLAT-12345"
NS_MAP = {"": "http://maven.apache.org/POM/4.0.0"}
COMMIT_MSG = 'updating project dependencies'

mock_pom_with_project_dependency = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${project.groupId}</groupId>
                <artifactId>mobile-applepay-service</artifactId>
                <version>${project.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>"""

mock_pom_with_project_group_id = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${project.groupId}</groupId>
                <artifactId>test-library-stubs</artifactId>
                <version>3.28.0</version>
                <scope>test</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>"""

mock_pom_with_com_rbs_group_id = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.rbs.digital.mobile</groupId>
                <artifactId>test-library-stubs</artifactId>
                <version>3.28.0</version>
                <scope>test</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>"""

mock_pom_with_test_jar = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.rbs.digital.mobile</groupId>
                <artifactId>test-library-stubs</artifactId>
                <version>3.28.0</version>
                <scope>test</scope>
                <type>test-jar</type>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>"""

mock_pom_with_just_parent = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>
</project>"""

mock_pom_with_missing_artifact_id = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.rbs.digital.mobile</groupId>
                <version>3.28.0</version>
                <scope>test</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>"""

mock_pom_with_missing_parent = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>
</project>"""


@pytest.fixture
def mock_git_service(mocker):
    return mocker.patch("tooling.common.git_service.GitService")


@pytest.fixture
def mock_nexus_service(mocker):
    return mocker.patch("tooling.updatedependencies.nexus_service.NexusService")


@pytest.fixture
def mock_repo(mocker: MockerFixture):
    return mocker.patch("dulwich.repo.Repo")


@pytest.fixture
def mock_temporary_directory(mocker):
    return mocker.patch("tempfile.TemporaryDirectory")


def get_parsed_root():
    ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")  # nosec
    xml_parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    pom = ET.parse(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', xml_parser)
    return pom.getroot()


def get_dependency_version():
    root = get_parsed_root()
    return root.find('dependencyManagement/dependencies/dependency[artifactId="test-library-stubs"]/version',
                     NS_MAP).text


def get_parent_version():
    root = get_parsed_root()
    return root.find('parent/version', NS_MAP).text


def test_should_ignore_dependencies_with_project_version(mock_temporary_directory,
                                                         mock_git_service,
                                                         mock_nexus_service,
                                                         mock_repo,
                                                         fs: FakeFilesystem):
    # given
    mock_git_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    fs.create_file(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', contents=mock_pom_with_project_dependency)
    mock_nexus_service.return_value.fetch_latest_version.return_value = '1.0.0'

    under_test = UpdateProjectDependenciesService(mock_git_service.return_value, mock_nexus_service.return_value)

    # when
    result = under_test.update(REPO_NAME, JIRA_NUMBER, 'some-branch')

    # then
    assert result == {
        "statusCode": 200,
        "body": "Not found new version of any dependency"
    }


@pytest.mark.parametrize(
    "pom_content",
    [
        mock_pom_with_project_group_id,
        mock_pom_with_com_rbs_group_id,
        mock_pom_with_test_jar
    ]
)
def test_should_update_dependency(mock_temporary_directory,
                                  mock_git_service,
                                  mock_nexus_service,
                                  mock_repo,
                                  fs: FakeFilesystem,
                                  pom_content: str):
    # given
    mock_git_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_git_service.return_value.create_merge_request.return_value = 'https://link-to-mr'
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    mock_nexus_service.return_value.fetch_latest_version.return_value = '3.100.0'

    fs.create_file(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', contents=pom_content)

    under_test = UpdateProjectDependenciesService(mock_git_service.return_value, mock_nexus_service.return_value)

    # when
    result = under_test.update(REPO_NAME, JIRA_NUMBER, 'some-branch')

    # then
    assert result == {
        "statusCode": 200,
        "body": "Merge request created with updated dependencies",
        "additionalInfo": {
            "mergeRequestUrl": "https://link-to-mr"
        }
    }

    mock_git_service.return_value.commit.assert_called_once_with(mock_repo.return_value, JIRA_NUMBER, COMMIT_MSG)
    mock_git_service.return_value.push.assert_called_once_with(mock_repo.return_value, REPO_NAME)

    mock_git_service.return_value.create_new_branch.assert_called_once()
    args, kwargs = mock_git_service.return_value.create_new_branch.call_args
    repo = args[0]
    branch_name = args[1]
    assert repo == mock_repo.return_value
    assert branch_name.startswith(f'feature/{JIRA_NUMBER}_update_dependencies_')

    assert get_dependency_version() == '3.100.0'


def test_should_not_update_dependency_when_already_latest(mock_temporary_directory,
                                                          mock_git_service,
                                                          mock_nexus_service,
                                                          mock_repo,
                                                          fs: FakeFilesystem):
    # given
    mock_git_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_git_service.return_value.create_merge_request.return_value = 'https://link-to-mr'
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    mock_nexus_service.return_value.fetch_latest_version.return_value = '3.28.0'

    fs.create_file(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', contents=mock_pom_with_com_rbs_group_id)

    under_test = UpdateProjectDependenciesService(mock_git_service.return_value, mock_nexus_service.return_value)

    # when
    result = under_test.update(REPO_NAME, JIRA_NUMBER, 'some-branch')

    # then
    assert result == {
        "statusCode": 200,
        "body": "Not found new version of any dependency"
    }


def test_should_update_parent(mock_temporary_directory,
                              mock_git_service,
                              mock_nexus_service,
                              mock_repo,
                              fs: FakeFilesystem):
    # given
    mock_git_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_git_service.return_value.create_merge_request.return_value = 'https://link-to-mr'
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    mock_nexus_service.return_value.fetch_latest_version.return_value = '3.200.0'

    fs.create_file(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', contents=mock_pom_with_just_parent)
    under_test = UpdateProjectDependenciesService(mock_git_service.return_value, mock_nexus_service.return_value)

    # when
    result = under_test.update(REPO_NAME, JIRA_NUMBER, 'some-branch')

    # then
    assert result == {
        "statusCode": 200,
        "body": "Merge request created with updated dependencies",
        "additionalInfo": {
            "mergeRequestUrl": "https://link-to-mr"
        }
    }
    mock_git_service.return_value.commit.assert_called_once_with(mock_repo.return_value, JIRA_NUMBER, COMMIT_MSG)
    mock_git_service.return_value.push.assert_called_once_with(mock_repo.return_value, REPO_NAME)

    mock_git_service.return_value.create_new_branch.assert_called_once()
    args, kwargs = mock_git_service.return_value.create_new_branch.call_args
    repo = args[0]
    branch_name = args[1]
    assert repo == mock_repo.return_value
    assert branch_name.startswith(f'feature/{JIRA_NUMBER}_update_dependencies_')

    assert get_parent_version() == '3.200.0'


def test_should_throw_error_when_missing_dependency_element(mock_temporary_directory,
                                                            mock_git_service,
                                                            mock_nexus_service,
                                                            mock_repo,
                                                            fs: FakeFilesystem):
    # given
    mock_git_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_git_service.return_value.create_merge_request.return_value = 'https://link-to-mr'
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    mock_nexus_service.return_value.fetch_latest_version.return_value = '3.200.0'

    fs.create_file(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', contents=mock_pom_with_missing_artifact_id)
    under_test = UpdateProjectDependenciesService(mock_git_service.return_value, mock_nexus_service.return_value)

    with pytest.raises(InternalServerError, match="Unexpected null XML element for type: artifactId"):
        under_test.update(REPO_NAME, JIRA_NUMBER, 'some-branch')


def test_should_throw_error_when_missing_parent(mock_temporary_directory,
                                                mock_git_service,
                                                mock_nexus_service,
                                                mock_repo,
                                                fs: FakeFilesystem):
    # given
    mock_git_service.return_value.clone_checkout.return_value = mock_repo.return_value
    mock_git_service.return_value.create_merge_request.return_value = 'https://link-to-mr'
    mock_temporary_directory.return_value.__enter__.return_value = LOCAL_DIR
    mock_nexus_service.return_value.fetch_latest_version.return_value = '3.200.0'

    fs.create_file(f'{LOCAL_DIR}/{REPO_NAME}/pom.xml', contents=mock_pom_with_missing_parent)
    under_test = UpdateProjectDependenciesService(mock_git_service.return_value, mock_nexus_service.return_value)

    with pytest.raises(InternalServerError, match="Could not find parent element in root pom.xml"):
        under_test.update(REPO_NAME, JIRA_NUMBER, 'some-branch')
