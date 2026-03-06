#version 430 core
in vec2 TexCoords;
out vec4 FragColor;

uniform vec2 u_resolution;
uniform vec2 u_jitter;
uniform vec3 u_camPos;
uniform vec3 u_camForward;
uniform vec3 u_camRight;
uniform vec3 u_camUp;

uniform float u_a;
uniform float u_M;

uniform vec3 u_sun1_pos;
uniform vec3 u_sun2_pos;
uniform vec3 u_sun1_color;
uniform vec3 u_sun2_color;

const int MAX_STEPS = 500; 

// maps blown-out hdr light back into standard monitor range
vec3 ACESFilm(vec3 x) {
    float a = 2.51; float b = 0.03; float c = 2.43; float d = 0.59; float e = 0.14;
    return clamp((x*(a*x+b))/(x*(c*x+d)+e), 0.0, 1.0);
}

// procedural hash starfield. much cheaper than sampling a cubemap.
float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1); p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

vec3 get_sky_color(vec3 dir) {
    vec3 final_sky = vec3(0.002);
    vec3 grid3 = floor(dir * 250.0);
    vec3 local3 = fract(dir * 250.0) - vec3(0.5);
    float star_hash = hash(grid3);
    if (star_hash > 0.985) { 
        vec3 offset = vec3(hash(grid3+1.0), hash(grid3+2.0), hash(grid3+3.0)) - 0.5;
        float dist = length(local3 - offset * 0.5);
        float star = smoothstep(0.25, 0.0, dist); 
        final_sky += vec3(1.0, 0.9, 0.8) * star * (star_hash - 0.985) * 600.0;
    }
    return final_sky;
}

// pure cartesian acceleration vector. 
// spherical boyer-lindquist caused fp32 precision collapse at the poles.
vec3 calc_accel(vec3 p) {
    float r = length(p);
    float r_sq = r * r;
    vec3 pull = -(p / r) * (u_M / r_sq);
    vec3 drag = cross(vec3(0.0, 1.0, 0.0), p / r) * (u_a * u_M / (r_sq * r));
    return pull + drag;
}

// 4th order runge-kutta. expensive, but strictly needed to curve light 360 deg without drift.
void step_RK4(inout vec3 p, inout vec3 v, float dt) {
    vec3 v1 = v;
    vec3 a1 = calc_accel(p);

    vec3 v2 = v + a1 * (dt * 0.5);
    vec3 a2 = calc_accel(p + v1 * (dt * 0.5));

    vec3 v3 = v + a2 * (dt * 0.5);
    vec3 a3 = calc_accel(p + v2 * (dt * 0.5));

    vec3 v4 = v + a3 * dt;
    vec3 a4 = calc_accel(p + v3 * dt);

    p += (v1 + 2.0 * v2 + 2.0 * v3 + v4) * (dt / 6.0);
    v = normalize(v + (a1 + 2.0 * a2 + 2.0 * a3 + a4) * (dt / 6.0));
}

// standard symplectic euler. use this in deep space to save fps.
void step_Euler(inout vec3 p, inout vec3 v, float dt) {
    vec3 a = calc_accel(p);
    v = normalize(v + a * dt);
    p += v * dt;
}

void main() {
    vec2 ndc = ((gl_FragCoord.xy / u_resolution.xy) + u_jitter) * 2.0 - 1.0;
    ndc.x *= u_resolution.x / u_resolution.y;
    vec3 rayDir = normalize(u_camForward + ndc.x * u_camRight + ndc.y * u_camUp);
    
    vec2 ndc_unjittered = (gl_FragCoord.xy / u_resolution.xy) * 2.0 - 1.0;
    ndc_unjittered.x *= u_resolution.x / u_resolution.y;
    vec3 skyDir = normalize(u_camForward + ndc_unjittered.x * u_camRight + ndc_unjittered.y * u_camUp);
    
    // analytical grid plane. skip calculation entirely if ray points up.
    vec3 grid_color = vec3(0.0);
    float grid_t = 9999.0;
    float t_plane = (-4.0 - u_camPos.y) / skyDir.y; 
    if (t_plane > 0.0) {
        float t = t_plane;
        for(int i = 0; i < 120; i++) {
            vec3 p = u_camPos + skyDir * t;
            float r = length(p.xz);
            float funnel_y = -8.0 - (12.0 * u_M) / max(r, 0.5);
            float dist = p.y - funnel_y;
            if (abs(dist) < 0.08) {
                grid_t = t;
                float angle = atan(p.z, p.x);
                if (fract(r * 0.5) < 0.06 || fract(angle * 12.0 / 3.14159) < 0.06) {
                    grid_color = vec3(0.0, 0.8, 1.5) * 4.0 * exp(-r * 0.02); 
                }
                break;
            }
            t += max(abs(dist) * 0.4, 0.05);
            if (t > 200.0) break;
        }
    }

    vec3 pos = u_camPos;
    vec3 dir = rayDir;
    
    bool hit_horizon = false;
    vec3 accum_color = vec3(0.0);
    float transmittance = 1.0;
    
    float r_plus = u_M + sqrt(max(u_M*u_M - u_a*u_a, 0.0));
    float rs = 2.0 * u_M; 
    float r_ph = 1.5 * rs; 
    float dt = 0.05; 
    
    for(int i = 0; i < MAX_STEPS; i++) {
        float r = length(pos);
        float r_sq = r * r;
        
        // cull the ray instantly if it crosses the event horizon
        if(r_sq <= (r_plus * r_plus * 1.01)) {
            hit_horizon = true; 
            break; 
        }
        if(r_sq > 10000.0) break;

        // relativistic volumetric integration
        if(r_sq > 100.0) {
            float d1_sq = dot(pos - u_sun1_pos, pos - u_sun1_pos);
            float d2_sq = dot(pos - u_sun2_pos, pos - u_sun2_pos);
            
            if(d1_sq < 900.0 || d2_sq < 900.0) {
                // doppler beaming. gas moving towards us blueshifts and gets significantly brighter.
                vec3 disk_vel = normalize(cross(vec3(0.0, 1.0, 0.0), pos)) * 0.4;
                float gamma = 1.0 / sqrt(1.0 - 0.4 * 0.4);
                float cosTheta = dot(normalize(disk_vel), -dir);
                float D = 1.0 / (gamma * (1.0 - 0.4 * cosTheta));
                float beaming = pow(D, 3.0);
                
                // gravitational redshift. stretches wavelength as it falls in.
                float redshift = sqrt(max(0.0, 1.0 - rs / r));

                if(d1_sq < 900.0) {
                    float glow = clamp(1.0 - (sqrt(d1_sq) / 30.0), 0.0, 1.0);
                    float density = glow * glow;
                    vec3 beamed_col = u_sun1_color * beaming;
                    beamed_col.r *= redshift; beamed_col.g *= pow(redshift, 1.2); beamed_col.b *= pow(redshift, 1.5);
                    accum_color += beamed_col * density * 0.15 * transmittance * dt;
                    transmittance *= clamp(1.0 - (density * 0.04 * dt), 0.0, 1.0); 
                }
                if(d2_sq < 900.0) {
                    float glow = clamp(1.0 - (sqrt(d2_sq) / 30.0), 0.0, 1.0);
                    float density = glow * glow;
                    vec3 beamed_col = u_sun2_color * beaming;
                    beamed_col.r *= redshift; beamed_col.g *= pow(redshift, 1.2); beamed_col.b *= pow(redshift, 1.5);
                    accum_color += beamed_col * density * 0.15 * transmittance * dt;
                    transmittance *= clamp(1.0 - (density * 0.04 * dt), 0.0, 1.0);
                }
            }
        }

        // multi-ring fractal cascade. explicitly rendering sub-rings for perfect sharpness.
        if (r > r_ph - 0.5 && r < r_ph + 0.5) {
            float b = length(cross(pos, dir));
            float bc = 3.0 * sqrt(3.0) * u_M;
            
            // only calculate for rays skimming the critical impact parameter
            if (abs(b - bc) < 0.8) {
                vec3 cascade_color = vec3(0.0);
                float cascade_opacity = 0.0;
                
                for(int j = 1; j < 5; j++) {
                    float n = float(j);
                    
                    // spread the rings further apart
                    float ring_b = bc + exp(-n * 1.5) * 1.2;
                    float dist_to_ring = abs(b - ring_b);
                    
                    // razor sharp lines
                    float sharpness = 400.0 * exp(n * 0.8); 
                    float glow = exp(-dist_to_ring * sharpness);
                    
                    // high intensity to punch through
                    float intensity = exp(-n * 0.8); 
                    
                    cascade_color += vec3(1.0, 0.85, 0.6) * glow * intensity * 25.0;
                    cascade_opacity += glow * intensity;
                }
                
                accum_color += cascade_color * transmittance * dt;
                // block background light so gaps stay dark
                transmittance *= clamp(1.0 - (cascade_opacity * dt * 15.0), 0.0, 1.0);
            }
        }

        // dynamic orbital brake. crush step size near photon sphere, open it up in deep space.
        float dist_to_ph = abs(r - r_ph);
        dt = min(0.05 + 0.2 * ((r - r_plus) / u_M), 3.0);
        
        if (r < u_M * 10.0) {
            float orbital_speed_limit = max(0.015, dist_to_ph * 0.15);
            dt = min(dt, orbital_speed_limit);
            step_RK4(pos, dir, dt);
        } else {
            step_Euler(pos, dir, dt);
        }
    }
    
    vec3 final_color = accum_color;
    float main_t = length(pos - u_camPos); 
    
    if (!hit_horizon) {
        final_color += get_sky_color(dir) * transmittance;
        main_t = 9999.0; 
    } 

    if (grid_color != vec3(0.0) && grid_t < main_t - 0.1) {
        final_color += grid_color * transmittance; 
    }

    FragColor = vec4(ACESFilm(final_color), 1.0);
}