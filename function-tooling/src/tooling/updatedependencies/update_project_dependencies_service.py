import tempfile
import time
import xml.etree.ElementTree as ET  # nosec
from xml.etree.ElementTree import ElementTree, Element  # nosec
from typing import Any
from packaging import version

from tooling.common.git_service import GitService
from tooling.updatedependencies.nexus_service import NexusService
from pylibrarycore.exceptions.exceptions import InternalServerError
from pylibrarycore.logging.logger_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class UpdateProjectDependenciesService:
    _ns_map = {
        "": "http://maven.apache.org/POM/4.0.0"
    }

    def __init__(self, git_service: GitService, nexus_service: NexusService) -> None:
        self._git_service = git_service
        self._nexus_service = nexus_service

    def update(self, repo_name: str, jira_number: str, branch: str) -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as local_dir:
            repo = self._git_service.clone_checkout(repo_name, local_dir, branch)
            is_updated = self.__update_dependencies(local_dir, repo_name)
            if is_updated:
                new_branch_name = f'feature/{jira_number}_update_dependencies_{time.time()}'
                self._git_service.create_new_branch(repo, new_branch_name)
                self._git_service.commit(repo, jira_number, "updating project dependencies")
                self._git_service.push(repo, repo_name)
                mr_link = self._git_service.create_merge_request(repo, repo_name, branch, jira_number)
                return {
                    "statusCode": 200,
                    "body": "Merge request created with updated dependencies",
                    "additionalInfo": {
                        "mergeRequestUrl": f'{mr_link}'
                    }
                }
            else:
                return {
                    "statusCode": 200,
                    "body": "Not found new version of any dependency"
                }

    def __update_dependencies(self, root_dir: str, repo_name: str) -> bool:
        pom = UpdateProjectDependenciesService.__parse_pom(root_dir, repo_name)
        root = pom.getroot()

        updated_count = 0

        parent = root.find('parent', UpdateProjectDependenciesService._ns_map)
        if not parent:
            raise InternalServerError("Could not find parent element in root pom.xml")
        updated_count += self.__update_dependency(parent)

        for dependency in root.findall('.//dependency', UpdateProjectDependenciesService._ns_map):
            updated_count += self.__update_dependency(dependency)

        if updated_count > 0:
            pom.write(f'{root_dir}/{repo_name}/pom.xml')
            return True
        else:
            return False

    def __update_dependency(self, dependency: Element) -> int:
        group_id = self.__get_dependency_element_text(dependency, 'groupId')
        artifact_id = self.__get_dependency_element_text(dependency, 'artifactId')
        current_version = self.__get_dependency_element_text(dependency, 'version')

        if group_id in ['com.rbs.digital.mobile', '${project.groupId}'] and current_version != '${project.version}':
            latest_version = self._nexus_service.fetch_latest_version(artifact_id)
            if latest_version and version.parse(latest_version) > version.parse(current_version):
                logger.info("Updating %s:%s from %s to %s",
                            group_id, artifact_id, current_version, latest_version)
                self.__get_dependency_element(dependency, 'version').text = latest_version
                return 1
        return 0

    @staticmethod
    def __parse_pom(root_dir: str, repo_name: str) -> ElementTree:
        ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")  # nosec
        xml_parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))  # nosec
        return ET.parse(f'{root_dir}/{repo_name}/pom.xml', xml_parser)  # nosec

    @staticmethod
    def __get_dependency_element_text(dependency: Element, element_type: str) -> str:
        element = UpdateProjectDependenciesService.__get_dependency_element(dependency, element_type)
        if element.text is None:
            raise InternalServerError(f"Element '{element_type}' has no text content")
        return element.text

    @staticmethod
    def __get_dependency_element(dependency: Element, element_type: str) -> Element:
        element = dependency.find(element_type, UpdateProjectDependenciesService._ns_map)
        if element is None:
            raise InternalServerError(f'Unexpected null XML element for type: {element_type}')
        return element
