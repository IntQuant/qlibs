#version 330

uniform mat4 mvp;

in vec2 pos;
in vec3 tpos;
in float z;

out vec3 mtpos;

void main() {
    gl_Position = mvp * vec4(pos, z, 1);
    mtpos = tpos;
}