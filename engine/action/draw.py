from engine.math.vector import normalize_length, rotate_vector, rotate_vector_2d


def set_draw_commands(self: object, value: list = [{}], **kwargs):
    """Draw textures on the screen. 'draw': [Texture, Texture, Texture]"""
    self.draw = value
    self.render_interruption = True


def apply_smear_effect(self: object, value: list = [{}], **kwargs):
    """Draw textures on the screen. 'draw': [Texture, Texture, Texture]"""
    self.draw += value
    self.render_interruption = True


def trigger_afterimage(self: object, value=any, **kwargs):
    """Draw the above images on the screen. 'Double_image': Any"""
    pass


def trigger_render_shake(
    self: object,
    value: dict = {
        "strength": 20,
        "direction": [0, 0],
        "duration": None,
        "damping": 6,
        "target": "self",
    },
    scene=None,
    **kwargs
):
    target = self if value.get("target", "self") == "self" else scene.camera
    if target == None:
        return

    rotate_function = rotate_vector_2d if target.dimension == 2 else rotate_vector

    target.draw_shake.trigger(
        strength=value.get("strength", 0.2),
        direction=rotate_function(
            angle=self.rotation,
            vector=normalize_length(
                vector=value.get("direction", [1, 1]), length=target.dimension
            ),
        ),
        duration=value.get("duration", 20),
        damping=value.get("damping", 6.0),
    )


def start_camera_path(self: object, value: list = [], **kwargs):
    """The path the camera will follow. 'Camera_path': ()"""
    return
    self.camera.path, self.camera.frame = {
        "path": tuple(value["path"]),
        "object": {
            "self": self,
            "other": self.rival,
            "global": self.app,
        }[value["object"]],
    }, [0, 0]


DRAW_ACT = {
    "draw": set_draw_commands,
    "smear": apply_smear_effect,
    "afterimage": trigger_afterimage,
    "draw_shake": trigger_render_shake,
}
