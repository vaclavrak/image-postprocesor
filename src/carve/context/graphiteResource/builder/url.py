"""

Created on 31. 1. 2014
refactored 16. 3. 2018

@author: Vena

"""


import urllib
from builtins import object
from .dimension import DimensionBuilder

def _escape_uri_val(val):
    return urllib.quote(val)



class GraphiteUrlBuilderException(Exception):
    pass


class GraphiteUrlBuilder(object):
    _url_prefix = ""
    _dimension = []
    _uriParamSeparator = "&"
    _untilT = "now"
    _fromT = "-1d"
    _format = "json"
    _allowedFormats = ['png', 'raw', 'csv', 'json', 'svg']
    _tz = "Europe/Prague"

    def __init__(self):
        self._format = None
        self._url_prefix = None

    def set_url_prefix(self, url_prefix : str) -> object:
        self._url_prefix = url_prefix
        return self

    def add_dimension(self, dim: DimensionBuilder) -> object:
        self._dimension.append(dim)
        return self

    @property
    def url(self):
        uri= [self.dimension, self.time_frame, self.data_format, self.tz]
        uri = filter(None, uri)
        params = self._uriParamSeparator.join(uri)
        return "%s?%s" % (self._url_prefix, params)

    @property
    def data_format(self) -> str:
        if self._format is None:
            raise GraphiteUrlBuilderException("No data format specified, call set_data_format first")
        return "format=%s" % self._format

    @property
    def time_frame(self):
        return "from={fromT}{sep}suntil={toT}".format(fromT = self._fromT, sep = self._uriParamSeparator,
                                                       toT = self._untilT)
    @property
    def dimension(self) -> str:
        ret_val = []
        for aDim in self._dimension:
            ret_val.append("target={}".format(aDim.make().url_encode()))
        ret_val = self._uriParamSeparator.join(ret_val)
        return ret_val

    @property
    def tz(self) -> str:
        return None if self._tz is None else "tz=%s" % self._tz

    def interval(self, from_time, to_time = 'now'):
        self.set_start_time(from_time)
        self.set_end_time(to_time)
        return self

    def set_data_format(self, data_format)-> object:
        if data_format not in self._allowedFormats:
            data_format = None
        self._format = data_format
        return self

    def set_timezone(self, tz : str)-> object:
        self._tz = tz
        return self

    def set_start_time(self, start_time : str)-> object:
        self._fromT = start_time
        return self

    def set_end_time(self, until_time : str) -> object:
        self._untilT = until_time
        return self
