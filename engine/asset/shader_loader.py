import os
import numpy


def create_2d_quad(ctx, program, size=(1.0, 1.0), position=(0.0, 0.0)):
    x, y = position
    w, h = size
    vertices = numpy.array(
        [
            x,
            y,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            x + w,
            y,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            x + w,
            y + h,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            x,
            y + h,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
        ],
        dtype="f4",
    )

    indices = numpy.array([0, 1, 2, 0, 2, 3], dtype="i4")

    vbo = ctx.buffer(vertices.tobytes())
    ibo = ctx.buffer(indices.tobytes())

    vao_content = [(vbo, "2f 2f 3f", "in_position", "in_texcoord", "in_normal")]

    vao = ctx.vertex_array(program, vao_content, index_buffer=ibo)
    return vao


def load_shaders(ctx, path):
    shader_programs = {}
    shader_dir = path + "/"
    for filename in os.listdir(shader_dir):
        if filename.endswith(".vert") or filename.endswith(".frag"):
            shader = os.path.splitext(filename)[0]
            if shader not in shader_programs:
                shader_programs[shader] = {}
                with open(path + "/" + shader + ".vert", "r") as f:
                    vertex_src = f.read()
                with open(path + "/" + shader + ".frag", "r") as f:
                    fragment_src = f.read()

                shader_programs[shader]["program"] = ctx.program(
                    vertex_shader=vertex_src,
                    fragment_shader=fragment_src,
                )
                common_uniforms = {"color_texture": 0, "shadow_map": 1}
                for uniform, slot in common_uniforms.items():
                    if uniform in shader_programs[shader]["program"]:
                        shader_programs[shader]["program"][uniform].value = slot
                shader_programs[shader]["params"] = {}
                for uname, uobj in shader_programs[shader]["program"]._members.items():
                    dtype = uobj.dimension
                    arrlen = uobj.array_length
                    if dtype in (1, 2, 3, 4) and arrlen == 1:
                        usage = ".value"
                    elif dtype in (9, 16):
                        usage = ".write"
                    else:
                        usage = ".value"
                    shader_programs[shader]["params"][uname] = {
                        "dtype": dtype,
                        "array_len": arrlen,
                        "usage": usage,
                    }
                shader_programs[shader]["quad"] = create_2d_quad(
                    ctx=ctx, program=shader_programs[shader]["program"]
                )
    return shader_programs
