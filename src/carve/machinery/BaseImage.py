from abc import ABCMeta, abstractmethod
from datetime import datetime
from django.utils import timezone
from logging import getLogger
import pytz
import time
from PIL import Image
from carve.Controller import Configurator

logger = getLogger("carve.machinery")


class BaseImageException(Exception):
    pass


class BaseImage(metaclass=ABCMeta):
    # PIL image instance
    _image_pil = None
    _time = 0
    _config = None

    def __init__(self):
        self._image_pil = None
        self._time = None
        self._config = None

    @property
    def time(self) -> datetime:
        return self._time

    def load_image(self, img_class: Image):
        self._image_pil = img_class
        return self

    @property
    def image(self) -> Image:
        return self._image_pil

    def set_time(self, tm: int):
        local_tz = pytz.timezone(str(timezone.get_default_timezone()))
        t = time.gmtime(tm)
        self._time = datetime(*t[:6], tzinfo=pytz.utc).astimezone(local_tz)
        tt = self._time.timetuple()
        self.config.set_context("second", tt.tm_sec)
        self.config.set_context("minute", tt.tm_min)
        self.config.set_context("hour", tt.tm_hour)
        self.config.set_context("day", tt.tm_mday)
        self.config.set_context("month", tt.tm_mon)
        self.config.set_context("year", tt.tm_year)
        self.config.set_context("wday", tt.tm_wday)
        self.config.set_context("yday", tt.tm_yday)
        self.config.set_context("zone", tt.tm_zone)
        self.config.set_context("gmtoff", tt.tm_gmtoff)
        self.config.set_context("isdst", tt.tm_isdst)
        self.config.set_context("create_image_ts", tm)
        return self

    def set_config(self, cfg: Configurator):
        if not isinstance(cfg, Configurator):
            raise BaseImageException("Invalid config object supplied.")
        self._config = cfg
        return self

    @property
    def config(self)-> Configurator:
        return self._config

    def save(self, fp, quality=60):
        self._image_pil.save(fp, quality=quality)
        return self