# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class Problem(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type='about:blank', title=None, status=None, detail=None, instance=None):  # noqa: E501
        """Problem - a model defined in OpenAPI

        :param type: The type of this Problem.  # noqa: E501
        :type type: str
        :param title: The title of this Problem.  # noqa: E501
        :type title: str
        :param status: The status of this Problem.  # noqa: E501
        :type status: int
        :param detail: The detail of this Problem.  # noqa: E501
        :type detail: str
        :param instance: The instance of this Problem.  # noqa: E501
        :type instance: str
        """
        self.openapi_types = {
            'type': str,
            'title': str,
            'status': int,
            'detail': str,
            'instance': str
        }

        self.attribute_map = {
            'type': 'type',
            'title': 'title',
            'status': 'status',
            'detail': 'detail',
            'instance': 'instance'
        }

        self._type = type
        self._title = title
        self._status = status
        self._detail = detail
        self._instance = instance

    @classmethod
    def from_dict(cls, dikt) -> 'Problem':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Problem of this Problem.  # noqa: E501
        :rtype: Problem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this Problem.

        An absolute URI that identifies the problem type.  When dereferenced, it SHOULD provide human-readable documentation for the problem type (e.g., using HTML).   # noqa: E501

        :return: The type of this Problem.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Problem.

        An absolute URI that identifies the problem type.  When dereferenced, it SHOULD provide human-readable documentation for the problem type (e.g., using HTML).   # noqa: E501

        :param type: The type of this Problem.
        :type type: str
        """

        self._type = type

    @property
    def title(self):
        """Gets the title of this Problem.

        A short, summary of the problem type. Written in english and readable for engineers (usually not suited for non technical stakeholders and not localized); example: Service Unavailable   # noqa: E501

        :return: The title of this Problem.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Problem.

        A short, summary of the problem type. Written in english and readable for engineers (usually not suited for non technical stakeholders and not localized); example: Service Unavailable   # noqa: E501

        :param title: The title of this Problem.
        :type title: str
        """

        self._title = title

    @property
    def status(self):
        """Gets the status of this Problem.

        The HTTP status code generated by the origin server for this occurrence of the problem.   # noqa: E501

        :return: The status of this Problem.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Problem.

        The HTTP status code generated by the origin server for this occurrence of the problem.   # noqa: E501

        :param status: The status of this Problem.
        :type status: int
        """
        if status is not None and status >= 600:  # noqa: E501
            raise ValueError("Invalid value for `status`, must be a value less than `600`")  # noqa: E501
        if status is not None and status < 100:  # noqa: E501
            raise ValueError("Invalid value for `status`, must be a value greater than or equal to `100`")  # noqa: E501

        self._status = status

    @property
    def detail(self):
        """Gets the detail of this Problem.

        A human readable explanation specific to this occurrence of the problem.   # noqa: E501

        :return: The detail of this Problem.
        :rtype: str
        """
        return self._detail

    @detail.setter
    def detail(self, detail):
        """Sets the detail of this Problem.

        A human readable explanation specific to this occurrence of the problem.   # noqa: E501

        :param detail: The detail of this Problem.
        :type detail: str
        """

        self._detail = detail

    @property
    def instance(self):
        """Gets the instance of this Problem.

        An absolute URI that identifies the specific occurrence of the problem. It may or may not yield further information if dereferenced.   # noqa: E501

        :return: The instance of this Problem.
        :rtype: str
        """
        return self._instance

    @instance.setter
    def instance(self, instance):
        """Sets the instance of this Problem.

        An absolute URI that identifies the specific occurrence of the problem. It may or may not yield further information if dereferenced.   # noqa: E501

        :param instance: The instance of this Problem.
        :type instance: str
        """

        self._instance = instance
# flake8: noqa
