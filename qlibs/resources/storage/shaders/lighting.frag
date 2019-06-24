#version 330

uniform sampler2D text;

in vec3 f_normal;
in vec2 v_uv;

uniform vec3 light_dir;
uniform vec3 light_col;

in vec3 v_vert;
out vec3 color;

void main() {
    //vec3 ld = light-v_vert;
    //float distance_sq = ld.x * ld.x + ld.y * ld.y + ld.z * ld.z;
    //float lum = (clamp(dot(normalize(light - v_vert), normalize(f_normal)), 0.0, 1.0) * 200 / (distance_sq))* 0.9 + 0.1;
    vec3 lum = light_col * clamp(-dot(light_dir, f_normal), 0.0, 0.9) + vec3(0.1);
    color = texture(text, v_uv).xyz  * lum;
}
