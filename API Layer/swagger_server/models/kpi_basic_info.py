# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.kpi_name import KPIName  # noqa: F401,E501
from swagger_server.models.kpiid import KPIID  # noqa: F401,E501
from swagger_server import util


class KPIBasicInfo(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, name_id: KPIID=None, description: KPIName=None, formula: str=None, category: str=None, unit: str=None):  # noqa: E501
        """KPIBasicInfo - a model defined in Swagger

        :param name_id: The name_id of this KPIBasicInfo.  # noqa: E501
        :type name_id: KPIID
        :param description: The description of this KPIBasicInfo.  # noqa: E501
        :type description: KPIName
        :param formula: The formula of this KPIBasicInfo.  # noqa: E501
        :type formula: str
        :param category: The category of this KPIBasicInfo.  # noqa: E501
        :type category: str
        :param unit: The unit of this KPIBasicInfo.  # noqa: E501
        :type unit: str
        """
        self.swagger_types = {
            'name_id': KPIID,
            'description': KPIName,
            'formula': str,
            'category': str,
            'unit': str
        }

        self.attribute_map = {
            'name_id': 'nameID',
            'description': 'description',
            'formula': 'formula',
            'category': 'category',
            'unit': 'unit'
        }
        self._name_id = name_id
        self._description = description
        self._formula = formula
        self._category = category
        self._unit = unit

    @classmethod
    def from_dict(cls, dikt) -> 'KPIBasicInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The KPIBasicInfo of this KPIBasicInfo.  # noqa: E501
        :rtype: KPIBasicInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name_id(self) -> KPIID:
        """Gets the name_id of this KPIBasicInfo.


        :return: The name_id of this KPIBasicInfo.
        :rtype: KPIID
        """
        return self._name_id

    @name_id.setter
    def name_id(self, name_id: KPIID):
        """Sets the name_id of this KPIBasicInfo.


        :param name_id: The name_id of this KPIBasicInfo.
        :type name_id: KPIID
        """

        self._name_id = name_id

    @property
    def description(self) -> KPIName:
        """Gets the description of this KPIBasicInfo.


        :return: The description of this KPIBasicInfo.
        :rtype: KPIName
        """
        return self._description

    @description.setter
    def description(self, description: KPIName):
        """Sets the description of this KPIBasicInfo.


        :param description: The description of this KPIBasicInfo.
        :type description: KPIName
        """

        self._description = description

    @property
    def formula(self) -> str:
        """Gets the formula of this KPIBasicInfo.

        the expression used to compute the KPI or null for KPIs that don't require additional computations.  # noqa: E501

        :return: The formula of this KPIBasicInfo.
        :rtype: str
        """
        return self._formula

    @formula.setter
    def formula(self, formula: str):
        """Sets the formula of this KPIBasicInfo.

        the expression used to compute the KPI or null for KPIs that don't require additional computations.  # noqa: E501

        :param formula: The formula of this KPIBasicInfo.
        :type formula: str
        """

        self._formula = formula

    @property
    def category(self) -> str:
        """Gets the category of this KPIBasicInfo.


        :return: The category of this KPIBasicInfo.
        :rtype: str
        """
        return self._category

    @category.setter
    def category(self, category: str):
        """Sets the category of this KPIBasicInfo.


        :param category: The category of this KPIBasicInfo.
        :type category: str
        """

        self._category = category

    @property
    def unit(self) -> str:
        """Gets the unit of this KPIBasicInfo.

        Unit of measurement  # noqa: E501

        :return: The unit of this KPIBasicInfo.
        :rtype: str
        """
        return self._unit

    @unit.setter
    def unit(self, unit: str):
        """Sets the unit of this KPIBasicInfo.

        Unit of measurement  # noqa: E501

        :param unit: The unit of this KPIBasicInfo.
        :type unit: str
        """

        self._unit = unit
