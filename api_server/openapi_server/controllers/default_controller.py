import connexion
import six

from openapi_server.models.build_status import BuildStatus  # noqa: E501
from openapi_server import util


def build_statuses_branch_branch_get(branch):  # noqa: E501
    """Get all branch build statuses

    Get a list of all build statuses from a specific branch # noqa: E501

    :param branch: A unique branch identifier
    :type branch: str

    :rtype: List[BuildStatus]
    """
    return 'do some magic!'


def build_statuses_get():  # noqa: E501
    """Get all build statuses

    Get a list of all build statuses # noqa: E501


    :rtype: List[BuildStatus]
    """
    return 'do some magic!'


def build_statuses_project_project_id_get(project_id, branch=None):  # noqa: E501
    """Get all project build statuses

    Get a list of all build statuses from a specific project # noqa: E501

    :param project_id: A unique project identifier
    :type project_id: str
    :param branch: A specific branch
    :type branch: str

    :rtype: List[BuildStatus]
    """
    return 'do some magic!'
