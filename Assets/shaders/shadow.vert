#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord;

uniform mat4 model;
uniform mat4 light_vp;

out vec2 frag_texcoord;

void main() {
    gl_Position = light_vp * model * vec4(in_position, 1.0);
    frag_texcoord = in_texcoord;
    in_normal;
}

