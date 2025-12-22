#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 frag_texcoord;

void main() {
    mat4 mv = view * model;
    vec4 view_position = mv * vec4(in_position, 1.0);
    gl_Position = projection * view_position;

    in_normal;

    frag_texcoord = in_texcoord;
}