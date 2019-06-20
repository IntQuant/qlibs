#version 330
        
uniform mat4 mvp;

uniform mat4 m;

in vec3 in_vert;
in vec3 normal;
in vec2 uv;

out vec3 v_vert;
out vec2 v_uv;
out vec3 f_normal;

void main() {
    vec4 t_vert = mvp * vec4(in_vert, 1.0);
    gl_Position = t_vert;
    v_vert = (m * vec4(in_vert, 1.0)).xyz;
    
    f_normal = (m * vec4(normal, 0)).xyz;
    v_uv = uv;
}
