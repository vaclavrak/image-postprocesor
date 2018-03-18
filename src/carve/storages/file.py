import os
from carve.storages.BaseStorage import BasicStorage


class file(BasicStorage):
    def __init__(self):
        super(file, self).__init__()
        self._file_name = None
        self._quality = None

    @property
    def file_name(self) -> str:
        fn = self.config.get_kv("{}/file_name".format(self.m))
        return fn

    @property
    def folder_name(self) -> str:
        fn = self.config.get_kv("{}/folder_name".format(self.m))
        return fn


    @property
    def quality(self) -> int:
        return self.config.get_kv("{}/quality".format(self.m), 60)

    def store(self):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
        fname = os.path.join(self.folder_name, self.file_name)
        fname = fname.format(**self.config.context)
        self.config.set_context("storage_file_name", fname)
        with open(fname, 'wb') as f:
            self.base_image.save(f, quality=self.quality )
        return self
