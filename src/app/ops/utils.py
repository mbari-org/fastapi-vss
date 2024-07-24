# fastapi-tator, Apache-2.0 license
# Filename: app/ops/utils.py
# Description: operations that modify the database

import os
import tator
from tator.openapi.tator_openapi import TatorApi
from typing import List
from app.logger import info, exception, debug, err
from app.ops.models import ProjectSpec, FilterType, LocClusterFilterModel

global projects


# Custom exceptions
class NotFoundException(Exception):
    def __init__(self, name: str):
        self._name = name


def init_api() -> tator.api:
    """
    Initialize the Tator API object. Requires TATOR_API_HOST and TATOR_API_TOKEN to be set in the environment.
    :return: Tator API object
    """
    if "TATOR_API_HOST" not in os.environ:
        exception("TATOR_API_HOST not found in environment variables!")
        raise Exception("TATOR_API_HOST not found in environment variables!")
        return
    if "TATOR_API_TOKEN" not in os.environ:
        exception("TATOR_API_TOKEN not found in environment variables!")
        raise Exception("TATOR_API_TOKEN not found in environment variables!")
        return

    try:
        api = tator.get_api(os.environ["TATOR_API_HOST"], os.environ["TATOR_API_TOKEN"])
        info(api)
        return api
    except Exception as e:
        exception(e)
        print(e)
        exit(-1)


def get_projects(tator_api: TatorApi):
    """
    Fetch the projects from the database
    :return:
    """
    global projects
    info("Fetching projects from tator")
    projects = tator_api.get_project_list()
    info(f"Found {len(projects)} projects")
    if len(projects) == 0:
        info("No projects found")
        return
    return projects


def get_version_id(api: tator.api, project_id: int, version_name: str) -> int:
    """
    Get the version id for the given version name. Returns None if the version is not found.
    :param api: The Tator API object
    :param project_id: The project id to search for the version in
    :param version_name: The name of the version to get the id for
    :return: The version id
    """
    versions = api.get_version_list(project_id)
    for v in versions:
        info(f"Found version {v.name} id {v.id} in project {project_id}")
        if v.name == version_name:
            return v.id

    return None


def get_project_spec(api: tator.api, project_name: str) -> ProjectSpec:
    """
    Get common project specifications used across operations. Raises a NotFoundException if the project is not found.
    :param project_name: The name of the project to initialize
    :return: The project spec
    """
    global projects

    project = next((p for p in projects if p.name == project_name), None)
    if project is None:
        info(f"Project {project_name} not found")
        raise NotFoundException(name=project_name)

    # Get the box localization type for the project
    localization_types = api.get_localization_type_list(project=project.id)

    # The box type is the one with the name 'Boxes'
    box_type = None
    for loc in localization_types:
        if loc.name == "Boxes" or loc.name == "Box":
            box_type = loc.id
            info(f"Found box type {box_type}")
            break

    # Get the image media type for the project
    media_types = api.get_media_type_list(project=project.id)
    image_type = None
    for m in media_types:
        info(f"Found media type {m.name} in project {project.name}")
        if m.name == "Images" or m.name == "Image":
            image_type = m.id
            info(f"Found image type {image_type}")
            break

    return ProjectSpec(project_name=project.name, project_id=project.id, image_type=image_type, box_type=box_type)


def get_media_ids(
        api: tator.api,
        spec: ProjectSpec,
        **kwargs
) -> List[int]:
    """
    Get the media ids that match the filter
    :param api:  tator api
    :param spec:  project specifications
    :param kwargs:  filter arguments to pass to the get_media_list function
    :return: list of media ids that match the filter
    """
    media_ids = []
    media_count = api.get_media_count(project=spec.project_id, type=spec.image_type)

    if media_count == 0:
        err(f"No media found in project {spec.project_name}")
        return media_ids

    batch_size = min(1000, media_count)
    debug(f"Searching through {media_count} medias with {kwargs}")
    for i in range(0, media_count, batch_size):
        media = api.get_media_list(project=spec.project_id, start=i, stop=i + batch_size, **kwargs)
        for m in media:
            media_ids.append(m.id)

    # Remove any duplicate ids
    media_ids = list(set(media_ids))

    debug(f"Found {len(media_ids)} medias with {kwargs}")
    return media_ids
