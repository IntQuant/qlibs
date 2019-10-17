#version 330

uniform mat4 mvp;

in vec2 pos;
in vec3 tpos;
in float z;
in vec4 tint;

out vec3 mtpos;
out vec4 fcolor;

void main() {
    gl_Position = mvp * vec4(pos, z, 1);
    mtpos = tpos;
    fcolor = tint;
}