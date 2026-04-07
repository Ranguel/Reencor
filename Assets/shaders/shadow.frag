#version 330

in vec2 frag_texcoord;

uniform sampler2D color_texture;
uniform bvec2 flip;

out float frag_depth;

void main() {
    vec2 uv = frag_texcoord;
    if (flip.x)
        uv.x = 1.0 - uv.x;
    if (!flip.y)
        uv.y = 1.0 - uv.y;
    vec4 color = texture(color_texture, uv);
    if (color.a < 0.1) discard;
    frag_depth = gl_FragCoord.z;
}