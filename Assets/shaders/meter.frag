#version 330

uniform vec4 tint;
uniform bool chess;

out vec4 frag_color;

void main() {
    if (chess) {
        ivec2 pixel = ivec2(gl_FragCoord.xy);
        if ((pixel.x + pixel.y) % 2 == 1)
            discard;
    }
    frag_color = tint;
}