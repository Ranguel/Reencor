#version 330

in vec2 in_position;
in vec2 in_texcoord;
in vec3 in_normal;

uniform vec2 position;
uniform vec2 size;
uniform bool side;
uniform float texture_aspect;

out vec2 frag_texcoord;

void main() {
    vec2 scaled_size = size;
    scaled_size.x = scaled_size.y * texture_aspect;
    vec2 pos = position;
    if(side) {
        pos.x = -pos.x - scaled_size.x;
    }
    gl_Position = vec4(in_position * scaled_size + pos, 0.0, 1.0);
    frag_texcoord = in_texcoord;
    in_normal;
}