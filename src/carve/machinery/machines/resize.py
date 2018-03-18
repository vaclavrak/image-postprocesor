
from carve.machinery.machines.BaseMachine import BaseMachine
from carve.machinery.BaseImage import BaseImage
from PIL import Image


class resize(BaseMachine):
    def __init__(self):
        super(resize, self).__init__()

    def carve(self) -> Image:
        w = self.config.get_kv("{}/resize/width".format(self.cp))
        h = self.config.get_kv("{}/resize/height".format(self.cp))
        self.config.set_context("width", w)
        self.config.set_context("height", h)
        return self.base_image.image.resize([w, h], Image.ANTIALIAS)
