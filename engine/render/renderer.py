import moderngl

from engine.render.window import Window


class Renderer:
    def __init__(self, resolution=(640, 400)):
        self.window = Window(resolution=(640, 400), frame_rate=60, vsync=True)

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        self.resolution = resolution
        self.aspect_ratio = self.resolution[0] / self.resolution[1]
        self.aspect_ratio_inv = self.resolution[1] / self.resolution[0]

        self.shader_programs = {}
        self.texture_dict = {}

        self.draw_queue = [{}, {}]

    def draw_texture(self, draw_call: dict):
        shader = draw_call.get("program", "lightning")
        disable_depth_test = draw_call.get("disable_depth_test", False)
        shadow_pass = draw_call.get("shadow_pass", False)

        for param in self.shader_programs[shader]["params"]:
            if param in draw_call:

                if param == "shadow_map":
                    draw_call[param].use(location=1)
                    continue
                elif param == "color_texture":
                    if draw_call[param] in self.texture_dict:
                        color_texture = self.texture_dict[draw_call[param]][0]
                    else:
                        color_texture = self.texture_dict["reencor/none"][0]
                    color_texture.use(location=0)
                    continue

                if param == "texture_aspect":
                    if draw_call[param] in self.texture_dict:
                        size_texture = self.texture_dict[draw_call[param]][1]
                    else:
                        size_texture = self.texture_dict["reencor/none"][1]
                    draw_call[param] = size_texture[0] / size_texture[1]

                meta = self.shader_programs[shader]["params"][param]
                dtype, usage = meta["dtype"], meta["usage"]

                if usage == ".value":
                    try:
                        self.shader_programs[shader]["program"][param].value = (
                            draw_call[param]
                        )
                    except Exception as e:
                        print(
                            f"Error setting shader parameter '{param}' with value '{draw_call[param]}': {e}"
                        )
                elif usage == ".write":
                    self.shader_programs[shader]["program"][param].write(
                        draw_call[param]
                    )

        if disable_depth_test and not shadow_pass:
            self.ctx.disable(moderngl.DEPTH_TEST)

        self.shader_programs[shader]["quad"].render()

        if disable_depth_test and not shadow_pass:
            self.ctx.enable(moderngl.DEPTH_TEST)

    def shadow_pass(self, camera: None, light: None, shadow: None):
        shadow.frame.clear()
        shadow.frame.use()

        light.vp = light.projection * light.view

        for draw_call in self.draw_queue:
            if draw_call.get("shadow_cast", False):
                self.draw_texture(
                    draw_call
                    | {
                        "program": "shadow",
                        "light_vp": light.vp,
                        "shadow_pass": True,
                    }
                )

    def light_pass(self, camera: None, light: None, shadow: None):
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
        camera: None,
        light: None,
        shadow: None,
        object_list: list = [],
        controllers: list = [],
        show_boxes: bool = False,
        show_input: bool = False,
        show_ui: bool = False,
    ):
        for object in object_list:
            self.draw_queue.extend(object.render())

        if show_boxes:
            for object in object_list:
                if hasattr(object, "draw_boxes"):
                    self.draw_queue.extend(object.draw_boxes())

        if show_input:
            for device in controllers:
                if hasattr(device, "render"):
                    self.draw_queue.extend(device.render())

        # --- Shadow Pass ---
        self.shadow_pass(camera, light, shadow)

        # --- Light Pass ---
        self.light_pass(camera, light, shadow)

        self.draw_queue.clear()
