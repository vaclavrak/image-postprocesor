from PIL import Image
from PIL import ImageDraw

from carve.machinery.machines.BaseMachine import BaseMachine


class alpha_square(BaseMachine):

    def carve(self)-> Image:
        for alpha_square_id in self.config.get_kvs("{}/alpha_square".format(self.cp)):
            r = self.config.get_kv("{}/alpha_square/{}/red".format(self.cp, alpha_square_id))
            g = self.config.get_kv("{}/alpha_square/{}/green".format(self.cp, alpha_square_id))
            b = self.config.get_kv("{}/alpha_square/{}/blue".format(self.cp, alpha_square_id))
            a = self.config.get_kv("{}/alpha_square/{}/alpha".format(self.cp, alpha_square_id))
            w = self.config.get_kv("{}/alpha_square/{}/width".format(self.cp, alpha_square_id))
            h = self.config.get_kv("{}/alpha_square/{}/height".format(self.cp, alpha_square_id))
            x = self.config.get_kv("{}/alpha_square/{}/topX".format(self.cp, alpha_square_id))
            y = self.config.get_kv("{}/alpha_square/{}/topY".format(self.cp, alpha_square_id))

            tmp = Image.new('RGBA', (w, h), (0,0,0,0))
            draw = ImageDraw.Draw(tmp)
            draw.rectangle([(0, 0), (w,h)], fill=(r,g,b,a))
            self.base_image.image.paste(tmp, (x,y), tmp)
        return self.base_image.image



