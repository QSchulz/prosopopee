import imagesize
import logging

from json import dumps as json_dumps
from pathlib import Path
from ruamel.yaml import YAML
from zlib import crc32

from .utils import remove_superficial_options

class ImageCommon():
    @property
    def ratio(self):
        width, height = self.size
        return width / height


class Thumbnail(ImageCommon):
    def __init__(self, base_filepath, base_id, size):
        self.filepath = self.__filepath(base_filepath, base_id, size)
        self.size = size

    def __filepath(self, base_filepath, base_id, size):
        p = Path(base_filepath)
        height, width = size
        suffix = '-{base_id}-{height}x{width}{suffix}'.format(
                base_id = base_id,
                height = height if height else '',
                width = width if width else '',
                suffix = p.suffix,
                )

        return p.parents[0] / (p.stem + suffix)


class BaseImage(ImageCommon):
    def __init__(self, options):
        self.size = imagesize.get(options['name'])
        self.filepath = options['name']
        self.options = remove_superficial_options(options)
        self.thumbnails = dict()
        self.chksum_opt = crc32(bytes(json_dumps(self.options, sort_keys=True), "utf-8"))

    def copy(self):
        return self.thumbnail(self.size)

    def thumbnail(self, size):
        thumbnail = Thumbnail(self.filepath, self.chksum_opt, size)
        return self.thumbnails.setdefault(thumbnail.filepath, thumbnail).filepath.name


# TODO: add support for looking into parent directories (name: ../other_gallery/pic.jpg)
class ImageFactory():
    base_imgs = dict()

    def get(self, path, image):
        if not isinstance(image, dict):
            image = { "name": image }

        if not "name" in image:
            yaml = YAML()
            logging.error("Image in {} does not have a `name` property, please add the "
            "filename of the image to a `name` property. To make it easy to find where it's "
            "missing, here are the other properties for this image:\n{}"
            .format(path + "/settings.yaml", yaml.dump(image)))
            sys.exit(1)

        image["name"] = Path(path).joinpath(image["name"])
        img = BaseImage(image)
        return self.base_imgs.setdefault(img.filepath / str(img.chksum_opt), img)

imageFactory = ImageFactory()
