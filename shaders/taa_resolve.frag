#version 430 core
in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D u_CurrentFrame;
uniform sampler2D u_HistoryBuffer;
uniform bool u_is_moving;

void main() {
    vec3 current = texture(u_CurrentFrame, TexCoords).rgb;
    vec3 history = texture(u_HistoryBuffer, TexCoords).rgb;
    
    // blend frames to kill volumetric noise. skip if moving to prevent ghosting.
    vec3 color = u_is_moving ? current : mix(history, current, 0.1);
    
    // dual-tap bloom. gaussian blur is too heavy for the framerate budget.
    vec2 texel = 1.0 / textureSize(u_CurrentFrame, 0);
    vec3 bloom = texture(u_CurrentFrame, TexCoords + vec2(texel.x * 2.0, 0.0)).rgb * 0.15;
    bloom += texture(u_CurrentFrame, TexCoords - vec2(texel.x * 2.0, 0.0)).rgb * 0.15;
    bloom += texture(u_CurrentFrame, TexCoords + vec2(0.0, texel.y * 2.0)).rgb * 0.15;
    bloom += texture(u_CurrentFrame, TexCoords - vec2(0.0, texel.y * 2.0)).rgb * 0.15;
    
    color += bloom * 0.5;
    
    FragColor = vec4(color, 1.0);
}