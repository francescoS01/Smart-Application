# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.user_role import UserRole  # noqa: F401,E501
from swagger_server import util


class UserBasicInfo(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, name: str=None, surename: str=None, username: str=None, email: str=None, role: UserRole=None):  # noqa: E501
        """UserBasicInfo - a model defined in Swagger

        :param name: The name of this UserBasicInfo.  # noqa: E501
        :type name: str
        :param surename: The surename of this UserBasicInfo.  # noqa: E501
        :type surename: str
        :param username: The username of this UserBasicInfo.  # noqa: E501
        :type username: str
        :param email: The email of this UserBasicInfo.  # noqa: E501
        :type email: str
        :param role: The role of this UserBasicInfo.  # noqa: E501
        :type role: UserRole
        """
        self.swagger_types = {
            'name': str,
            'surename': str,
            'username': str,
            'email': str,
            'role': UserRole
        }

        self.attribute_map = {
            'name': 'name',
            'surename': 'surename',
            'username': 'username',
            'email': 'email',
            'role': 'role'
        }
        self._name = name
        self._surename = surename
        self._username = username
        self._email = email
        self._role = role

    @classmethod
    def from_dict(cls, dikt) -> 'UserBasicInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UserBasicInfo of this UserBasicInfo.  # noqa: E501
        :rtype: UserBasicInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """Gets the name of this UserBasicInfo.


        :return: The name of this UserBasicInfo.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this UserBasicInfo.


        :param name: The name of this UserBasicInfo.
        :type name: str
        """

        self._name = name

    @property
    def surename(self) -> str:
        """Gets the surename of this UserBasicInfo.


        :return: The surename of this UserBasicInfo.
        :rtype: str
        """
        return self._surename

    @surename.setter
    def surename(self, surename: str):
        """Sets the surename of this UserBasicInfo.


        :param surename: The surename of this UserBasicInfo.
        :type surename: str
        """

        self._surename = surename

    @property
    def username(self) -> str:
        """Gets the username of this UserBasicInfo.


        :return: The username of this UserBasicInfo.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username: str):
        """Sets the username of this UserBasicInfo.


        :param username: The username of this UserBasicInfo.
        :type username: str
        """

        self._username = username

    @property
    def email(self) -> str:
        """Gets the email of this UserBasicInfo.


        :return: The email of this UserBasicInfo.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this UserBasicInfo.


        :param email: The email of this UserBasicInfo.
        :type email: str
        """

        self._email = email

    @property
    def role(self) -> UserRole:
        """Gets the role of this UserBasicInfo.


        :return: The role of this UserBasicInfo.
        :rtype: UserRole
        """
        return self._role

    @role.setter
    def role(self, role: UserRole):
        """Sets the role of this UserBasicInfo.


        :param role: The role of this UserBasicInfo.
        :type role: UserRole
        """

        self._role = role
