#version 330 core

in vec2 texf;
out vec4 color;

uniform sampler2D text;
uniform vec3 text_color;

void main() {
    color = vec4(text_color, texture(text, texf).r);
}
