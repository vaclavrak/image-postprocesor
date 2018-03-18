from abc import ABCMeta, abstractmethod
from carve.Controller import Configurator
from carve.machinery.BaseImage import BaseImage, BaseImageException


class BaseMachineException(Exception):
    pass


class BaseMachine(object):
    _config = None
    _base_image = None
    _m = None

    def __init__(self):
        self._config = None
        self._base_image = None
        self._m = None

    def set_config(self, cfg: Configurator):
        if not isinstance(cfg, Configurator):
            raise BaseMachineException("Invalid config object supplied.")
        self._config = cfg
        return self

    def set_base_image(self, bi: BaseImage) -> object:
        self._base_image = bi
        return self

    @property
    def cp(self):
        return "machineries/{}/decorations".format(self.m)

    @property
    def m(self):
        if not self._m:
            raise BaseMachineException("No machine found, call set_machine first.")
        return self._m

    def set_machine(self, m: str) -> object:
        self._m = m
        return self

    @property
    def config(self) -> Configurator:
        return self._config

    @property
    def base_image(self) -> BaseImage:
        if self._base_image is None:
            self._base_image = BaseImage()
        return self._base_image


    @abstractmethod
    def carve(self) -> object:
        pass
