from abc import ABCMeta, abstractmethod
from carve.Controller import Configurator
from logging import getLogger

logger = getLogger("carve.context")


class BaseContextException(Exception):
    pass


class BaseContext(object):
    _context = {}
    _config = None
    _m = None

    def __init__(self):
        self._context = {}
        self._config = None
        self._m = None

    def set_config(self, cfg: Configurator):
        if not isinstance(cfg, Configurator):
            raise BaseContextException("Invalid config type")
        self._config = cfg
        return self

    @property
    def config(self) -> Configurator:
        return self._config

    def set_context(self, k, v):
        self.config.set_context(k, v)
        return self

    @abstractmethod
    def prepare_context(self) -> object:
        pass


    @property
    def m(self):
        if not self._m:
            raise BaseContextException("No prefix found, call set_prefix first.")
        return self._m

    def set_prefix(self, m: str) -> object:
        self._m = m
        return self
