from carve.sources.Source import BaseSource, BaseSourceException, logger
import time
import inotify.adapters
from PIL import Image
from datetime import datetime
import os
import re


class folder_watch(BaseSource):
    start_time = None
    _i = None
    _reg_ex = None

    def __init__(self):
        super(folder_watch, self).__init__()
        self._rrm = None
        self.start_time = None
        self.stop_flag = False
        self._i = False
        self._reg_ex = None

    @property
    def source(self):
        source = self.config.get_kv('source/folder_watch/source', None)
        if source is None:
            raise BaseSourceException("No `source` specified 'source/folder_watch/source'")
        return source

    @property
    def reg_ex(self):
        if self._reg_ex is None:
            reg_ex = self.config.get_kv("source/folder_watch/filter_reg_ex")
            self._reg_ex = re.compile(reg_ex )
        return self._reg_ex

    def is_my_file(self, fname):
        return True if self.reg_ex.search(fname) else False

    def process_folder(self, event):
        if event is None:
            return
        (header, type_names, watch_path, filename) = event


        if 'IN_CLOSE_WRITE' not in type_names:
            return self

        if not filename:
            return self

        if not self.is_my_file(filename):
            return self

        logger.info("WD=(%d) MASK=(%d) COOKIE=(%d) LEN=(%d) MASK->NAMES=%s "
            "WATCH-PATH=[%s] FILENAME=[%s]",
            header.wd, header.mask, header.cookie, header.len, type_names,
            watch_path, filename)

        path = os.path.join(watch_path, filename)
        with open(path, "rb") as f:
            self.load_from_file(f)
            self.config.make_context()
            self.work_with_image()
        return self

    def load_from_file(self, fp):
        self.base_image.load_image(Image.open(fp))
        self.base_image.set_time(time.time())
        return self

    def start(self):
        self.start_time = time.time()
        self.stop_flag = False
        self._i = inotify.adapters.Inotify()
        try:
            self._i.add_watch(self.source)
            while self.stop_flag is False:
                for event in self._i.event_gen():
                    self.process_folder(event)
                    if self.stop_flag is True:
                        break

        except Exception as e:
            logger.exception(e)
        finally:
            if self._i:
                self._i.remove_watch(self.source)
                self._i = None
        return self

    def stop(self):
        self.stop_flag = True
        if self._i:
            self._i.remove_watch(self.source)
            self._i = None
        self.start_time = None
        logger.info("Connection closed")
        return self



