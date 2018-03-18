import sys
from abc import ABCMeta, abstractmethod
from logging  import getLogger
from carve.machinery.BaseImage import BaseImage
from carve.Controller import Configurator
from carve.storages.BaseStorage import BasicStorage
from PIL import Image
from django.conf import settings
logger = getLogger("carve.sources")


class BaseSourceException(Exception):
    pass


class BaseMachine(object):
    _config = None
    _bi = None
    _m = None
    _bi_original = None

    def __init__(self):
        self._config = None
        self._bi = None
        self._m = None
        self._bi_original = None
        self._img_original = None

    @property
    def config(self) -> Configurator:
        return self._config

    @property
    def base_image(self) -> BaseImage:
        if self._bi is None:
            self._bi = BaseImage()
        return self._bi

    def load_original(self, img : Image):
        self._img_original = img
        self.base_image.load_image(img.copy())
        return self

    @property
    def original(self) -> Image:
        if self._img_original is None:
            raise BaseSourceException("No original image set, call  load_original first")
        return self._img_original

    def set_config(self, cfg: Configurator):
        if not isinstance(cfg, Configurator):
            raise BaseSourceException("Invalid config type")
        self._config = cfg
        self.base_image.set_config(cfg)
        return self

    def storage(self) -> BasicStorage:
        orders = self.config.get_kv("{}/order_storages".format(self.cp), settings.DEFAULT_STORAGE_OPRDER).split(",")
        for order in orders:
            store = self.config.get_kv("{}/storages/{}".format(self.cp, order), None)
            if store is None:
                continue
            __import__("carve.storages.{cls}".format(cls=order))
            src_module = sys.modules["carve.storages.{cls}".format(cls=order)]
            src_class = getattr(src_module, order)
            stor = src_class().set_config(self.config).set_prefix("machineries/{}/storages/{}".format(self.m, order))
            stor.base_image.load_image(self.base_image.image)
            yield stor

    def store(self):
        for s in self.storage():
            s.store()
        return self

    def set_machine(self, m):
        self._m = m
        return self

    @property
    def cp(self):
        return "machineries/{}".format(self.m)

    @property
    def m(self):
        if not self._m:
            raise BaseSourceException("No machine found, call set_machine first.")
        return self._m

    def machinery(self):
        orders = self.config.get_kv("{}/order".format(self.cp), settings.DEFAULT_DECORATION_OPRDER).split(",")
        self.base_image.load_image(self.original.copy())
        for order in orders:
            decoration = self.config.get_kv("{}/decorations/{}".format(self.cp, order), None)
            if decoration is None:
                continue
            __import__("carve.machinery.machines.{cls}".format(cls=order))
            src_module = sys.modules["carve.machinery.machines.{cls}".format(cls=order)]
            src_class = getattr(src_module, order)
            src = src_class()
            src.set_config(self.config).set_machine(self.m).base_image.load_image(self.base_image.image)
            yield src

    def carve(self):
        for cm in self.machinery():
            self.base_image.load_image(cm.carve())
        return self


class BaseSource(metaclass=ABCMeta):
    _config = None
    _bi = None

    def __init__(self):
        self._config = None
        self._bi = None

    def set_config(self, cfg: Configurator):
        if not isinstance(cfg, Configurator):
            raise BaseSourceException("Invalid config type")
        self._config = cfg
        self.base_image.set_config(cfg)
        return self

    @property
    def config(self) -> Configurator:
        return self._config

    @property
    def base_image(self) -> BaseImage:
        if self._bi is None:
            self._bi = BaseImage()
        return self._bi

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def work_with_image(self):
        try:
            for m in self.config.get_kvs("machineries"):
                bm = BaseMachine().set_config(self.config).set_machine(m)
                bm.load_original(self._bi.image)
                bm.carve()
                bm.store()
            return self
        except Exception as e:
            logger.exception(e)
            raise e