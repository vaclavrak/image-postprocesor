"""
read data from graphite
"""

__author__ = 'rak'

import urllib
import json
from http.client import  HTTPException
from carve.context.graphiteResource.builder.url import GraphiteUrlBuilder
from carve.context.graphiteResource.builder.dimension import DimensionBuilder
from carve.context.BaseContext import BaseContext, logger


class GraphiteException(Exception):
    pass


class graphite(BaseContext):


    _urlBuilder = None
    _response = None

    def __init__(self):
        self._urlBuilder = None
        self._response = None

    @property
    def url_builder(self) -> GraphiteUrlBuilder:
        if self._urlBuilder is None:
            self._urlBuilder = GraphiteUrlBuilder()
        return self._urlBuilder

    def cleanup(self) -> object:
        self._urlBuilder = None
        return self

    def format(self, format):
        self.url_builder.set_data_format(format)
        return self

    def prepare_context(self) -> dict:
        url = self.config.get_kv("{}/url".format(self.m))
        starttime = self.config.get_kv("{}/starttime".format(self.m))
        endtime = self.config.get_kv("{}/endtime".format(self.m)).format(**self.config.context)
        self.cleanup()
        self.url_builder.set_url_prefix(url)
        self.url_builder.set_start_time(starttime)
        self.url_builder.set_end_time(endtime)
        self.url_builder.set_data_format("json")
        dims = []
        for d in self.config.get_kvs("{}/dimension".format(self.m)):
            d_str = d.get("dimension", None)
            if d_str:
                dims.append(d)
                self.url_builder.add_dimension(DimensionBuilder().set_dimension(d_str))
                k = d.get("name")
                self.config.set_context(k, d.get("default", None))

        if len(dims) == 0:
            logger.warning("No dimension found.")
            return self
        try:
            url_t = self.url_builder.url
            req = urllib.request.Request(url_t)
            req.add_header('Content-Type',  'application/json')
            with urllib.request.urlopen(req) as f:
                json_data = json.loads(f.read().decode("utf-8"))

            dims.reverse()
            for d in dims:
                k = d.get("name")
                try:
                    ln = json_data.pop()
                    v = list(filter(None, [v[0] for v in ln.get('datapoints')]))[-1]
                except Exception:
                    v = d.get("default", None)
                self.config.set_context(k, v)
        except urllib.error.HTTPError as e:
            logger.error("Error reading `{}`, {}".format(url_t, e))
        except urllib.error.URLError as e:
            logger.error("Error reading `{}`, {}".format(url_t, e))
        except HTTPException as e:
            logger.error("Error reading `{}`, {}".format(url_t, e))

        return self

