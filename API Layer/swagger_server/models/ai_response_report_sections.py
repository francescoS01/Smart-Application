# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class AIResponseReportSections(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, key_performance_metrics: List[str]=None, overall_trends: List[str]=None, observations: List[str]=None):  # noqa: E501
        """AIResponseReportSections - a model defined in Swagger

        :param key_performance_metrics: The key_performance_metrics of this AIResponseReportSections.  # noqa: E501
        :type key_performance_metrics: List[str]
        :param overall_trends: The overall_trends of this AIResponseReportSections.  # noqa: E501
        :type overall_trends: List[str]
        :param observations: The observations of this AIResponseReportSections.  # noqa: E501
        :type observations: List[str]
        """
        self.swagger_types = {
            'key_performance_metrics': List[str],
            'overall_trends': List[str],
            'observations': List[str]
        }

        self.attribute_map = {
            'key_performance_metrics': 'Key Performance Metrics',
            'overall_trends': 'Overall Trends',
            'observations': 'Observations'
        }
        self._key_performance_metrics = key_performance_metrics
        self._overall_trends = overall_trends
        self._observations = observations

    @classmethod
    def from_dict(cls, dikt) -> 'AIResponseReportSections':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AIResponse_report_sections of this AIResponseReportSections.  # noqa: E501
        :rtype: AIResponseReportSections
        """
        return util.deserialize_model(dikt, cls)

    @property
    def key_performance_metrics(self) -> List[str]:
        """Gets the key_performance_metrics of this AIResponseReportSections.


        :return: The key_performance_metrics of this AIResponseReportSections.
        :rtype: List[str]
        """
        return self._key_performance_metrics

    @key_performance_metrics.setter
    def key_performance_metrics(self, key_performance_metrics: List[str]):
        """Sets the key_performance_metrics of this AIResponseReportSections.


        :param key_performance_metrics: The key_performance_metrics of this AIResponseReportSections.
        :type key_performance_metrics: List[str]
        """

        self._key_performance_metrics = key_performance_metrics

    @property
    def overall_trends(self) -> List[str]:
        """Gets the overall_trends of this AIResponseReportSections.


        :return: The overall_trends of this AIResponseReportSections.
        :rtype: List[str]
        """
        return self._overall_trends

    @overall_trends.setter
    def overall_trends(self, overall_trends: List[str]):
        """Sets the overall_trends of this AIResponseReportSections.


        :param overall_trends: The overall_trends of this AIResponseReportSections.
        :type overall_trends: List[str]
        """

        self._overall_trends = overall_trends

    @property
    def observations(self) -> List[str]:
        """Gets the observations of this AIResponseReportSections.


        :return: The observations of this AIResponseReportSections.
        :rtype: List[str]
        """
        return self._observations

    @observations.setter
    def observations(self, observations: List[str]):
        """Sets the observations of this AIResponseReportSections.


        :param observations: The observations of this AIResponseReportSections.
        :type observations: List[str]
        """

        self._observations = observations
