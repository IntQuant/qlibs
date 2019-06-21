#version 330 core

in vec2 pos;
in vec2 tex;

out vec2 texf;

uniform mat4 mvp;

void main() {
    gl_Position = mvp * vec4(pos, 0, 1);
    texf = tex;
}