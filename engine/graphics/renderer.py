import moderngl

from engine.graphics.window import Window
from engine.graphics.camera import Camera
from engine.graphics.light import Light
from engine.graphics.shadow import ShadowMap


class Renderer:
    def __init__(self, resolution=(640, 400)):
        self.window = Window(resolution=(640, 400), frame_rate=60, vsync=True)

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        self.resolution = resolution
        self.aspect_ratio = self.resolution[0] / self.resolution[1]
        self.aspect_ratio_inv = self.resolution[1] / self.resolution[0]

        self.camera = Camera(self.aspect_ratio, 0.1)
        self.light = Light(size=14)
        self.shadow = ShadowMap(ctx=self.ctx, size=1024)

        self.shader_programs = {}

        self.draw_queue = [{}, {}]

    def draw_texture(self, draw_call: dict):
        shader = draw_call.get("program", "lightning")
        disable_depth_test = draw_call.get("disable_depth_test", False)
        shadow_pass = draw_call.get("shadow_pass", False)

        for param in self.shader_programs[shader]["params"]:
            if param in draw_call:
                if param == "color_texture":
                    draw_call[param].use(location=0)
                    continue
                elif param == "shadow_map":
                    draw_call[param].use(location=1)
                    continue
                meta = self.shader_programs[shader]["params"][param]
                dtype, usage = meta["dtype"], meta["usage"]
                if usage == ".value":
                    self.shader_programs[shader]["program"][param].value = draw_call[
                        param
                    ]
                elif usage == ".write":
                    self.shader_programs[shader]["program"][param].write(
                        draw_call[param]
                    )

        if disable_depth_test and not shadow_pass:
            self.ctx.disable(moderngl.DEPTH_TEST)

        self.shader_programs[shader]["quad"].render()

        if disable_depth_test and not shadow_pass:
            self.ctx.enable(moderngl.DEPTH_TEST)

    def shadow_pass(self, camera: Camera, light: Light, shadow: ShadowMap):
        shadow.frame.clear()
        shadow.frame.use()

        light.vp = light.projection * light.view

        for draw_call in self.draw_queue:
            if draw_call.get("shadow_cast", False):
                self.draw_texture(
                    draw_call
                    | {
                        "program": "shadow",
                        # "view": camera.view,
                        # "projection": camera.projection,
                        # "light_pos": light.position,
                        "light_vp": light.vp,
                        "shadow_pass": True,
                    }
                )

    def light_pass(self, camera: Camera, light: Light, shadow: ShadowMap):
        self.ctx.screen.clear()
        self.ctx.screen.use()

        for draw_call in self.draw_queue:
            self.draw_texture(
                draw_call
                | {
                    "view": camera.view,
                    "projection": camera.projection,
                    "light_vp": light.vp,
                    "shadow_map": shadow.depth,
                    "screen_size": self.resolution,
                    "screan_aspect": self.aspect_ratio,
                    "screen_aspect_inv": self.aspect_ratio_inv,
                }
            )

    def render(
        self,
        object_list: list = [],
        input_device_list: list = [],
        draw_boxes: bool = False,
        draw_input: bool = False,
    ):
        for object in object_list:
            object.render(self, self.camera.position)

        if draw_boxes:
            for object in object_list:
                object.draw_boxes()

        if draw_input:
            for device in input_device_list:
                device.render(self)

        # --- Shadow Pass ---
        self.shadow_pass(self.camera, self.light, self.shadow)

        # --- Light Pass ---
        self.light_pass(self.camera, self.light, self.shadow)

        self.draw_queue.clear()
