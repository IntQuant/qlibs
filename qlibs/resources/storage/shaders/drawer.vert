#version 330
        
uniform mat4 mvp;

in vec3 in_vert;
in vec4 color;

out vec4 f_color;

void main() {
    gl_Position = mvp * vec4(in_vert, 1);
    f_color = color;
}

