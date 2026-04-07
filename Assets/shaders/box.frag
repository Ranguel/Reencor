#version 330

in vec2 frag_texcoord;

uniform vec4 color;
uniform float transparent;
uniform vec2 size;
uniform float border_thickness;

out vec4 frag_color;

void main() {
    vec2 frag_pixel = frag_texcoord * size;
    float dist_left   = frag_pixel.x;
    float dist_right  = size.x - frag_pixel.x;
    float dist_bottom = frag_pixel.y;
    float dist_top    = size.y - frag_pixel.y;

    float min_dist = min(min(dist_left, dist_right), min(dist_bottom, dist_top));

    if (min_dist < border_thickness) {
        frag_color = vec4(color.rgb, 1.0);
    } else {
        frag_color = vec4(color.rgb, transparent);
    }
}

