import glm
import moderngl


class ShadowMap:
    def __init__(self, size: int = 1024, ctx: moderngl.create_context = None):
        self.ctx = ctx
        self.size = (size, size)
        self.depth = self.ctx.depth_texture(self.size)
        self.depth.compare_func = ""
        self.depth.repeat_x = False
        self.depth.repeat_y = False
        self.fbo = self.ctx.framebuffer(depth_attachment=self.depth)
        self.color = self.ctx.texture(self.size, components=4)
        self.frame = self.ctx.framebuffer(
            color_attachments=[self.color],
            depth_attachment=self.depth,
        )
        self.bias = glm.mat4(
            0.5,
            0.0,
            0.0,
            0.0,
            0.0,
            0.5,
            0.0,
            0.0,
            0.0,
            0.0,
            0.5,
            0.0,
            0.5,
            0.5,
            0.5,
            1.0,
        )
