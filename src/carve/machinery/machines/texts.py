

from carve.machinery.machines.BaseMachine import BaseMachine
from carve.machinery.BaseImage import logger
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class texts(BaseMachine):

    def carve(self)-> Image:
        for txt_id in self.config.get_kvs("{}/texts".format(self.cp)):

            font_size = self.config.get_kv("{}/texts/{}/font_size".format(self.cp, txt_id), 10)
            line_height = self.config.get_kv("{}/texts/{}/line_height".format(self.cp, txt_id), 10)
            x = self.config.get_kv("{}/texts/{}/x".format(self.cp, txt_id))
            y = self.config.get_kv("{}/texts/{}/y".format(self.cp, txt_id))
            font_file = self.config.get_kv("{}/texts/{}/font_file".format(self.cp, txt_id))
            text_color = self.config.context.get("text_color", 0xFF00FF)
            position = (x, y)

            draw = ImageDraw.Draw(self.base_image.image)
            font = ImageFont.truetype(font_file, font_size, encoding='unic')
            i = 0
            for ln in self.config.get_kvs("{}/texts/{}/lines".format(self.cp, txt_id)):
                try:
                    tx = ln.format(**self.config.context)
                except KeyError as e:
                    logger.error(str(e))
                    tx = ln
                draw.text([position[0], position[1] + i * line_height], tx, text_color, font=font )
                i += 1

        return self.base_image.image