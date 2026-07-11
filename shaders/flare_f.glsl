#version 300 es
precision highp float;

out vec4 fragColor;
uniform float osg_FrameTime;

in vec2 v_uv;

float hash12(vec2 pos) {
    vec3 p3 = fract(vec3(pos.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float noise(vec2 n) {
    vec4 b = vec4(floor(n), ceil(n));
    vec2 f = smoothstep(vec2(0.0), vec2(1.0), fract(n));
    return mix(mix(hash12(b.xy), hash12(b.zy), f.x), mix(hash12(b.xw), hash12(b.zw), f.x), f.y);
}

float fbm(vec2 x) {
    float v = 0.0;
    float a = 0.4;

    for (int i = 0; i < 8; i++) {
        v += a * noise(x);
        x = x * 2.0;
        a *= 0.6;
    }
    return v;
}

float random(vec2 fv, float d1, float d2, float r) {
    return fract(sin(dot(fv, vec2(d1, d2))) * r);
}


void main(){
    vec2 center_pos = vec2(0.5, 0.5);
    float dist_to_sun = length(v_uv - center_pos);

    // Determining the size and extent of Light.
    // To expand or contract the flare, adjust the value 0.23.
    // float flare_base = 0.23 / (dist_to_sun + 0.065);
    float flare_base = 0.23 / (dist_to_sun + 0.065);
   
    // Make it fade out gradually.
    // if the value of 2.4 is increased, the result will be a sharp ring; if decreased, will be a foggy, blurry glow.
    float flare_glow = pow(flare_base, 2.4);

    float sun_wave = noise(v_uv * 5.0 - osg_FrameTime * 0.5);
    flare_glow += flare_glow * sun_wave * 0.12;
    
    vec3 core_white = vec3(1.0, 1.0, 1.0) * pow(flare_glow, 2.0) * 0.8; 
    vec3 outer_gold = vec3(1.0, 0.6, 0.18) * flare_glow;          

    vec3 flare_color = clamp(core_white + outer_gold, 0.0, 1.05);
    // If increase the size of the sun, increase the starting point (now, 0.18) of smoothstep (the position where the light begins to fade).
    // float alpha = 1.0 - smoothstep(0.1, 0.52, dist_to_sun);
    float alpha = 1.0 - smoothstep(0.18, 0.55, dist_to_sun);

    fragColor = vec4(flare_color, alpha);
}