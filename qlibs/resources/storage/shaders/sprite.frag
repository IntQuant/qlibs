#version 330

uniform sampler2DArray text;

in vec3 mtpos;
in vec4 fcolor;
out vec4 color;

void main() {
    color = texture(text, mtpos) * fcolor;
    if (color.a<0.001) discard;
}
