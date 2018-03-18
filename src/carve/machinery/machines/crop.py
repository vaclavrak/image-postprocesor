
from carve.machinery.machines.BaseMachine import BaseMachine
from carve.machinery.BaseImage import BaseImage
from PIL import Image


class crop(BaseMachine):

    def carve(self) -> Image:
        x = self.config.get_kv("{}/crop/x".format(self.cp))
        y = self.config.get_kv("{}/crop/y".format(self.cp))
        w = self.config.get_kv("{}/crop/width".format(self.cp))
        h = self.config.get_kv("{}/crop/height".format(self.cp))
        return self.base_image.image.crop((x,y,x+w,y+h))
