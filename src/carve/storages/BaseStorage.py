#
# very basic image storage
#
from abc import ABCMeta, abstractmethod
from carve.machinery.BaseImage import BaseImage
from carve.Controller import Configurator


class BasicStorageException(Exception):
    pass


class BasicStorage(object):
    _config = None
    _base_image = None
    _m = None

    def __init__(self):
        self._config = None
        self._base_image = None
        self._m = None

    @property
    def m(self):
        if not self._m:
            raise BasicStorageException("No storage found, call set_prefix first.")
        return self._m

    def set_prefix(self, m: str) -> object:
        self._m = m
        return self

    @property
    def base_image(self) -> BaseImage:
        if self._base_image is None:
            self._base_image = BaseImage()
        return self._base_image

    def set_config(self, cfg: Configurator) -> object:
        if not isinstance(cfg, Configurator):
            raise BasicStorageException("Invalid config object supplied.")
        self._config = cfg
        return self

    @property
    def config(self) -> Configurator:
        return self._config

    @abstractmethod
    def store(self):
        pass
