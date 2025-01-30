
"""
    This module contains the class ParameterFormatter to parse the parameters from the headers of the request.
"""

from datetime import datetime

class ParameterFormatter:
    """
        Class to handle the parameters from the headers of the request.

        :param content: The content of the request.
        :type content: dict
        :param param_name: The name of the parameter to get from the headers.
        :type param_name: str
    """
    def __init__(self, content, param_name):
        self._x = content.headers.get(param_name, None)

    def as_string(self):
        """
            Returns the parameter as a string.

            :return: The parameter as a string.
            :rtype: str
        """
        return self._x
    
    def as_int(self):
        """
            Returns the parameter as an integer.

            :return: The parameter as an integer.
            :rtype: int
        """
        return int(self._x) if self._x else None

    def as_float(self):
        """
            Returns the parameter as a float.

            :return: The parameter as a float.
            :rtype: float
        """
        return float(self._x) if self._x else None
    
    def as_datetime(self):
        """
            Returns the parameter as a datetime from a string formatted as '%Y-%m-%d %H:%M:%S'.

            :return: The parameter as a datetime.
            :rtype: datetime
        """
        return datetime.strptime(self._x, '%Y-%m-%d %H:%M:%S') if self._x else None
    
    # Returns a set of strings without duplicates
    def as_list_of_string(self):
        """
            Returns the parameter as a set of strings without duplicates.

            :return: The parameter as a set of strings without duplicates.
            :rtype: List[str]
        """
        return list(set(self._x.split(','))) if self._x else None

    # Returns a set of integers without duplicates
    def as_list_of_int(self):
        """
            Returns the parameter as a set of integers without duplicates.

            :return: The parameter as a set of integers without duplicates.
            :rtype: List[int]
        """
        return list(set([int(x) for x in self._x.split(',')])) if self._x else None
    
    # Returns a list of floats without duplicates
    def as_list_of_float(self):
        """
            Returns the parameter as a list of floats without duplicates.

            :return: The parameter as a list of floats without duplicates.
            :rtype: List[float]
        """
        return list(set([float(x) for x in self._x.split(',')])) if self._x else None
    
    def as_datetime_from_date(self):
        """
            Returns the parameter as a datetime from a string formatted as '%Y-%m-%d'.

            :return: The parameter as a datetime.
            :rtype: datetime
        """
        return datetime.strptime(self._x, '%Y-%m-%d') if self._x else None
    
    def as_bool(self):
        """
            Returns the parameter as a boolean.

            :return: The parameter as a boolean.
            :rtype: bool
        """
        return self._x.lower() == 'true' if self._x else None