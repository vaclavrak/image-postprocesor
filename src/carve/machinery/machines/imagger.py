from PIL import Image
from carve.machinery.machines.BaseMachine import BaseMachine


class imagger(BaseMachine):

    def carve(self)-> Image:
        for imgger_id in self.config.get_kvs("{}/imagger".format(self.cp)):
            source = self.config.get_kv("{}/imagger/{}/source".format(self.cp, imgger_id))
            w = self.config.get_kv("{}/imagger/{}/width".format(self.cp, imgger_id))
            h = self.config.get_kv("{}/imagger/{}/height".format(self.cp, imgger_id))
            x = self.config.get_kv("{}/imagger/{}/topX".format(self.cp, imgger_id))
            y = self.config.get_kv("{}/imagger/{}/topY".format(self.cp, imgger_id))
            img2img=Image.open(source)
            img2img=img2img.resize((w, h), Image.ANTIALIAS)
            self.base_image.image.paste(img2img, (x,y), img2img)
        return self.base_image.image



