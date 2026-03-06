// legacy fallback: grid is now computed analytically inside the raytracer
#version 430 core
layout (location = 0) in vec3 aPos;

uniform vec3 u_camPos;
uniform vec3 u_camForward;
uniform vec3 u_camRight;
uniform vec3 u_camUp;

out vec3 vPos;

void main() {
    vPos = aPos;
    vec3 offset = aPos - u_camPos;
    
    float x = dot(offset, u_camRight);
    float y = dot(offset, u_camUp);
    float z = dot(offset, -u_camForward);
    
    gl_Position = vec4(x * 1.5, y * 1.5 - 0.5, z * 0.5, -z);
}