#version 330

in vec2 frag_texcoord;

uniform sampler2D color_texture;
uniform vec4 tint;

out vec4 frag_color;

void main() {
    vec2 uv = frag_texcoord;
    uv.y = 1.0 - uv.y;
    vec4 color = texture(color_texture, uv);
    if(color.a < 0.1)
        discard;
    frag_color = color * tint;
}
