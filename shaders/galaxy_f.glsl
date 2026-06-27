#version 300 es
precision highp float;

out vec4 fragColor;
uniform float osg_FrameTime;
uniform vec2 u_resolution;


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
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 uv_aspect = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    
    // ###############
    // create nebula
    // ###############
    vec2 nebula_uv = uv_aspect * 1.2 + vec2(osg_FrameTime * 0.003, osg_FrameTime * 0.001);
    
    float n1 = fbm(uv_aspect * 1.5 + vec2(osg_FrameTime * 0.002, 0.0));
    float n2 = fbm(uv_aspect * 3.0 - vec2(0.0, osg_FrameTime * 0.001));
    
    float nebula_noise = mix(n1, n2, 0.4);
    float mask_outer = smoothstep(0.45, 0.70, nebula_noise);
    float mask_inner = smoothstep(0.55, 0.75, nebula_noise);

    vec3 nebula_color = vec3(0.08, 0.04, 0.20) * mask_outer; // 広がる深い紫
    nebula_color += vec3(0.18, 0.05, 0.15) * mask_inner;   // 中心にいくほど鮮やかなマゼンタ

    // ###############
    // create solar flare
    // ###############
    vec2 sun_pos = vec2(0.0, 0.0); 
    float dist_to_sun = length(uv_aspect - sun_pos);

    // Determining the size and extent of Light.
    // To expand or contract the flare, adjust the value 0.085.
    float flare_base = 0.085 / (dist_to_sun + 0.045);
    
    // Make it fade out gradually.
    // if the value of 2.8 if increased, the result will be a sharp ring; if decreased, will be a foggy, blurry glow.
    float flare_glow = pow(flare_base, 2.8);
    float sun_wave = noise(uv_aspect * 5.0 - osg_FrameTime * 0.5);
    flare_glow += flare_glow * sun_wave * 0.12;

    vec3 core_white = vec3(1.0, 1.0, 1.0) * pow(flare_glow, 2.0) * 0.8; 
    vec3 outer_gold = vec3(1.0, 0.6, 0.18) * flare_glow;          

    vec3 flare_color = clamp(core_white + outer_gold, 0.0, 1.05);

    // ###############
    // create starts
    // ###############
    vec2 sv = uv + osg_FrameTime * .0005;

    vec2 iv1 = floor(sv * 500.0);
    vec2 iv2 = floor(sv * 300.0);
    vec2 iv3 = floor(sv * 400.0);

    vec3 cell_noise1 = vec3(random(iv1, 12.0, 80.0, 4000.0));
    vec3 cell_noise2 = vec3(random(iv2, 12.333, 13.0, 5000.0));
    vec3 cell_noise3 = vec3(random(iv3, 90.4325, 12.0, 2000.0));
    vec3 cell_noise = ((cell_noise1 + cell_noise2 + cell_noise3) * .333 - .9) * 10.0;

    vec2 fv_s = uv * 20.0;
    vec2 fv = fract(vec2(fv_s.x + sin(osg_FrameTime * .005) * 10.0, fv_s.y + cos(osg_FrameTime * .005) * 10.0) * 0.5);
    vec3 circle = vec3(1.0 - smoothstep(length(fv - .25), .0, (sin(uv.x * 40.0) * cos(uv.y * 50.0)) * .015)); 
    vec3 final_starts = circle + clamp(cell_noise, .0, 1.0);

    fragColor = vec4(final_starts + nebula_color + flare_color, 1.0);
}