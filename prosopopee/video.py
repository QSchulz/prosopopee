import ffmpeg
from pathlib import Path

class MediaCommon():
    def __init__(self, filepath, size):
        self.filepath = filepath
        self.size = size

#    def __hash__(self):
#        return hash(self.filepath)

#    def __eq__(self, other):
#        if not isinstance(other, MediaCommon):
#            return NotImplemented
#        return self.filepath == other.filepath

    @property
    def ratio(self):
        width, height = self.size
        return width / height

class Thumbnail(MediaCommon):
    # Pass original filepath which the thumbnail will be based on, the filepath
    # to the actual file will be auto-generated depending on the size.
    def __init__(self, orig_filepath, size, **options):
        filepath = self.__filepath(orig_filepath, size, **options)
        super().__init__(filepath, size)
        print("requesting thumb of %s for %s: %s => %s" % (size, orig_filepath, filepath, self.filepath))
        #TODO: for cache support, we most likely will just want to hash the options
        self.options = options

    def __filepath(self, filepath, size, **options):
        p = Path(filepath)
        height, width = size
        suffix = '-{height}x{width}{suffix}'.format(
                height = height if height else '',
                width = width if width else '',
                suffix = SETTINGS["extension"],
                )

        return p.parents[0] / (p.stem + suffix)

class VideoOrig(MediaCommon):
    def __init__(self, orig_filepath):
        probe = ffmpeg.probe(orig_filepath)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        size = (int(video_stream['width']), int(video_stream['height']))
        super().__init__(orig_filepath, size)
        self.thumbnails = dict()

    def copy(self):
        return self.filepath.stem + ".webm"

    def thumbnail(self, size):
        thumbnail = Thumbnail(self.filepath, size)
        return self.thumbnails.setdefault(thumbnail.filepath, thumbnail).filepath.name

class VideoFactory():
    orig_video = dict()

    def get(self, path, filename):
        filepath = Path(path).joinpath(filename["name"])
        orig = VideoOrig(filepath)
        return self.orig_video.setdefault(orig.filepath, orig)

videoFactory = VideoFactory()
