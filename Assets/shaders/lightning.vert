#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 light_vp;
uniform vec2 uv_scale;

out vec3 frag_position;
out vec3 frag_normal;
out vec4 frag_shadowcoord;
out vec2 frag_texcoord;

void main() {
    mat4 mv = view * model;
    vec4 view_position = mv * vec4(in_position, 1.0);
    gl_Position = projection * view_position;

    frag_normal = mat3(mv) * normalize(in_normal);
    frag_position = view_position.xyz;
    frag_shadowcoord = light_vp * model * vec4(in_position, 1.0);
    frag_texcoord = in_texcoord * uv_scale;
}