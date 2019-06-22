#version 330

in vec4 f_color;
out vec3 color;

void main() {
    color = f_color.xyz;
}

