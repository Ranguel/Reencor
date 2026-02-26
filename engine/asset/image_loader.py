import moderngl
import numpy
import os
from PIL import Image


def make_asset_key(root, filename):
    return (root.rsplit("/", 1)[-1] + "/" + filename).rsplit(".", 1)[0]


def load_image_texture(
    ctx: moderngl.Context, path: str = "", texture_filter: str = "NEAREST"
):
    image = Image.open(path).convert("RGBA")
    data = numpy.array(image, dtype=numpy.uint8)

    texture = ctx.texture(data.shape[1::-1], 4, data.tobytes())
    texture.build_mipmaps()

    if texture_filter == "NEAREST":
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    elif texture_filter == "LINEAR":
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    elif texture_filter == "LINEAR_MIPMAP_LINEAR":
        texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    elif texture_filter == "NEAREST_MIPMAP_LINEAR":
        texture.filter = (moderngl.NEAREST_MIPMAP_LINEAR, moderngl.LINEAR)

    return texture, image.size


def load_images(ctx, path):
    images = {}
    for root, _, files in os.walk(path):
        for name in files:
            if name.lower().endswith((".png", ".jpg", ".jpeg")):
                key = make_asset_key(root, name)
                images[key] = load_image_texture(ctx, os.path.join(root, name))
    return images
