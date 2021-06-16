# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from openapi_server import util
from openapi_server.models.base_model_ import Model


class IAMAnomaly(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(
        self,
        active=None,
        created_at=None,
        id=None,
        member=None,
        project_id=None,
        role=None,
        updated_at=None,
    ):  # noqa: E501
        """IAMAnomaly - a model defined in OpenAPI

        :param active: The active of this IAMAnomaly.  # noqa: E501
        :type active: bool
        :param created_at: The created_at of this IAMAnomaly.  # noqa: E501
        :type created_at: datetime
        :param id: The id of this IAMAnomaly.  # noqa: E501
        :type id: str
        :param member: The member of this IAMAnomaly.  # noqa: E501
        :type member: str
        :param project_id: The project_id of this IAMAnomaly.  # noqa: E501
        :type project_id: str
        :param role: The role of this IAMAnomaly.  # noqa: E501
        :type role: str
        :param updated_at: The updated_at of this IAMAnomaly.  # noqa: E501
        :type updated_at: datetime
        """
        self.openapi_types = {
            "active": bool,
            "created_at": datetime,
            "id": str,
            "member": str,
            "project_id": str,
            "role": str,
            "updated_at": datetime,
        }

        self.attribute_map = {
            "active": "active",
            "created_at": "created_at",
            "id": "id",
            "member": "member",
            "project_id": "project_id",
            "role": "role",
            "updated_at": "updated_at",
        }

        self._active = active
        self._created_at = created_at
        self._id = id
        self._member = member
        self._project_id = project_id
        self._role = role
        self._updated_at = updated_at

    @classmethod
    def from_dict(cls, dikt) -> "IAMAnomaly":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The IAMAnomaly of this IAMAnomaly.  # noqa: E501
        :rtype: IAMAnomaly
        """
        return util.deserialize_model(dikt, cls)

    @property
    def active(self):
        """Gets the active of this IAMAnomaly.


        :return: The active of this IAMAnomaly.
        :rtype: bool
        """
        return self._active

    @active.setter
    def active(self, active):
        """Sets the active of this IAMAnomaly.


        :param active: The active of this IAMAnomaly.
        :type active: bool
        """

        self._active = active

    @property
    def created_at(self):
        """Gets the created_at of this IAMAnomaly.


        :return: The created_at of this IAMAnomaly.
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this IAMAnomaly.


        :param created_at: The created_at of this IAMAnomaly.
        :type created_at: datetime
        """

        self._created_at = created_at

    @property
    def id(self):
        """Gets the id of this IAMAnomaly.


        :return: The id of this IAMAnomaly.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this IAMAnomaly.


        :param id: The id of this IAMAnomaly.
        :type id: str
        """

        self._id = id

    @property
    def member(self):
        """Gets the member of this IAMAnomaly.


        :return: The member of this IAMAnomaly.
        :rtype: str
        """
        return self._member

    @member.setter
    def member(self, member):
        """Sets the member of this IAMAnomaly.


        :param member: The member of this IAMAnomaly.
        :type member: str
        """

        self._member = member

    @property
    def project_id(self):
        """Gets the project_id of this IAMAnomaly.


        :return: The project_id of this IAMAnomaly.
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this IAMAnomaly.


        :param project_id: The project_id of this IAMAnomaly.
        :type project_id: str
        """

        self._project_id = project_id

    @property
    def role(self):
        """Gets the role of this IAMAnomaly.


        :return: The role of this IAMAnomaly.
        :rtype: str
        """
        return self._role

    @role.setter
    def role(self, role):
        """Sets the role of this IAMAnomaly.


        :param role: The role of this IAMAnomaly.
        :type role: str
        """

        self._role = role

    @property
    def updated_at(self):
        """Gets the updated_at of this IAMAnomaly.


        :return: The updated_at of this IAMAnomaly.
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this IAMAnomaly.


        :param updated_at: The updated_at of this IAMAnomaly.
        :type updated_at: datetime
        """

        self._updated_at = updated_at


# flake8: noqa
