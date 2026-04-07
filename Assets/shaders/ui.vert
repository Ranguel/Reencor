#version 330

in vec2 in_position;
in vec2 in_texcoord;
in vec3 in_normal;

uniform vec2 position;
uniform vec2 size;
uniform vec2 uv_scale;
uniform vec2 uv_offset;
uniform vec2 uv_size;
uniform float screen_aspect_inv;
uniform float texture_aspect;
uniform bool side;
uniform bool keep_aspect;

out vec2 frag_texcoord;

void main() {
    vec2 scaled_size = size;
    if (keep_aspect) {
        scaled_size.x = scaled_size.y * texture_aspect * screen_aspect_inv;
    }
    vec2 pos = position;
    if (side) {
        pos.x = -pos.x - scaled_size.x;
    }
    gl_Position = vec4(in_position * scaled_size + pos, 0.0, 1.0);
    frag_texcoord = uv_offset + in_texcoord * uv_size * uv_scale;
    in_normal;
}