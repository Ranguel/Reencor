from .image_loader import load_images
from .sound_loader import load_sounds
from .object_loader import load_objects
from .shader_loader import load_shaders


class AssetManager:
    def __init__(self, ctx, path: str = ""):
        self.ctx = ctx
        self.images = {}
        self.sounds = {}
        self.objects = {}
        self.shaders = {}

        self.load_all(path)

    def load_all(self, base_path):
        self.shaders = load_shaders(self.ctx, base_path + "/shaders")
        self.images = load_images(self.ctx, base_path + "/images")
        self.sounds = load_sounds(base_path + "/sounds")
        self.objects = load_objects(base_path + "/objects")

    def unload(self):
        self.images.clear()
        self.sounds.clear()
        self.objects.clear()
        self.shaders.clear()
