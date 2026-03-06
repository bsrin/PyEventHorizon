// legacy fallback: grid is now computed analytically inside the raytracer
#version 430 core
in vec3 vPos;
out vec4 FragColor;

void main() {
    float fade = exp(-length(vPos.xz) * 0.02);
    FragColor = vec4(0.0, 0.5, 1.0, 1.0) * fade; 
    gl_FragDepth = 0.5; 
}