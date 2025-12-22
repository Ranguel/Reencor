#version 330

in vec2 frag_texcoord;
in vec3 frag_position;
in vec3 frag_normal;
in vec4 frag_shadowcoord;

uniform sampler2D shadow_map;
uniform sampler2D color_texture;
uniform vec3 light_pos;
uniform bvec2 flip;
uniform vec4 tint;

out vec4 frag_color;

void main() {
    vec2 uv = frag_texcoord;
    if (flip.x)
        uv.x = 1.0 - uv.x;
    if (!flip.y)
        uv.y = 1.0 - uv.y;
    vec4 color = texture(color_texture, uv);
    if (color.a < 0.1) discard;
    
    vec3 shadow_ndc = frag_shadowcoord.xyz / frag_shadowcoord.w;
    shadow_ndc = shadow_ndc * 0.5 + 0.5;
    float visibility = 0.0;
    vec3 light_dir = normalize(light_pos - frag_position);
    float diff = abs(dot(normalize(frag_normal), light_dir));

    if (shadow_ndc.z > 1.0 || shadow_ndc.x < 0.0 || shadow_ndc.x > 1.0 || shadow_ndc.y < 0.0 || shadow_ndc.y > 1.0) {
        visibility = 1.0;
    } else {
        float bias = max(0.005 * (1.0 - dot(frag_normal, light_dir)), 0.0005);
        float depth = texture(shadow_map, shadow_ndc.xy).r;
        visibility = (shadow_ndc.z - bias) > depth ? 0.5 : 1.0;
    }

    frag_color = color * tint * (0.25 + diff * 0.9) * visibility;
}