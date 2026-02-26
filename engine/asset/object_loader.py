import os
import json
from copy import deepcopy


DEFAULT_OBJECT = {
    "type": "projectile",
    "name": "empty",
    "portrait": "reencor/none",
    "palette": [],
    "music": "",
    "scale": [1, 1, 1],
    "gravity": [0, 0, 0],
    "mass": 1,
    "physics_type": "dynamic",
    "timekill": False,
    "meters": {
        "health": {"inicial": 1, "max": 1, "rate": 1},
        "super": {"inicial": 1, "max": 1, "rate": 1},
        "stamina": {"inicial": 1, "max": 1, "rate": 1},
    },
    "defaults": {
        "draw": {
            "folder": "",
            "name": "",
            "position": [0, 0, 0],
            "size": [0, 0, 0],
            "rotation": [0, 0, 0],
            "side": False,
            "flip": [False, False],
            "tint": [1, 1, 1, 1],
            "uv_offset": [0, 0],
            "uv_size": [1, 1],
            "uv_scale": [1, 1],
            "keep_aspect": False,
            "glow": 0,
            "shadow_cast": True,
            "disable_depth_test": False,
            "program": "lightning",
        },
        "boxes": {
            "hurtbox": {"rects": []},
            "hitbox": {"rects": [], "hitreg": []},
            "takebox": {"rects": []},
            "grabbox": {"rects": []},
            "pushbox": {"rects": []},
            "triggerbox": {"rects": [], "hitreg": []},
            "environmentbox": {
                "rects": [{"vec": [-0.23, 3.17, 0.69, 0.72]}],
                "grounded_friction": 0.7,
                "airborne": 0.1,
            },
        },
    },
    "combo_trails": [],
    "states": {},
}


def make_asset_key(root, filename, base):
    rel = os.path.relpath(os.path.join(root, filename), base)
    return rel.replace("\\", "/").rsplit(".", 1)[0]


def deep_merge_override(dest, source):
    for key, value in source.items():
        if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
            deep_merge_override(dest[key], value)
        else:
            dest[key] = value
    return dest


def load_objects(path):
    objects = {}
    for root, _, files in os.walk(path):
        for name in files:
            if name.lower().endswith(".json"):
                key = make_asset_key(root, name, path)
                with open(os.path.join(root, name), encoding="utf-8") as f:
                    objects[key] = deep_merge_override(
                        deepcopy(DEFAULT_OBJECT), json.load(f)
                    )
    return objects
