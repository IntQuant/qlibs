#version 330

uniform sampler2DArray text;

in vec3 mtpos;
out vec4 color;

void main() {
    color = texture(text, mtpos);
}
