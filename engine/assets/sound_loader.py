import os
from pygame import mixer


def make_asset_key(root, filename, base):
    rel = os.path.relpath(os.path.join(root, filename), base)
    return rel.replace("\\", "/").rsplit(".", 1)[0]


def load_sounds(path):
    sounds = {}
    for root, _, files in os.walk(path):
        for name in files:
            if name.lower().endswith((".wav", ".ogg", ".mp3")):
                key = make_asset_key(root, name, path)
                sounds[key] = mixer.Sound(os.path.join(root, name))
    return sounds
