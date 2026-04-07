#version 330

in vec2 in_position;
in vec2 in_texcoord;
in vec3 in_normal;

uniform vec2 position;
uniform vec2 size;
uniform bool side;

void main() {
    vec2 pos = position;
    if (side) {
        pos.x = -pos.x - size.x;
    }
    gl_Position = vec4(in_position * size + pos, 0.0, 1.0);
    in_texcoord;
    in_normal;
}