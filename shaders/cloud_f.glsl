#version 300 es
precision highp float;

out vec4 fragColor;
uniform float osg_FrameTime;

in vec2 v_uv;
in vec3 v_normal;
in vec3 v_view_dir;


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
    float a = 0.5;
    for (int i = 0; i < 5; i++) {
        v += a * noise(x);
        x = x * 2.0;
        a *= 0.5;
    }
    return v;
}

void main(){
    vec2 cloud_uv = v_uv * 4.0 + vec2(osg_FrameTime * 0.005, osg_FrameTime * 0.002);
    float cloud_noise = fbm(cloud_uv);

    // When making the gaps between the clouds more transparent, reduce the value of 0.40 to something like 0.30 or 0.25.  
    // When making the clouds more densely, increase the value of 0.40 to 0.45 or 0.50.
    float cloud_mask = 1.0 - smoothstep(0.50, 0.65, cloud_noise);

    // Calculate the dot product of the line of sight and the surface normal (the degree to which it faces forward)
    float v_dot_n = dot(normalize(v_view_dir), normalize(v_normal));
    float fresnel_edge = clamp(v_dot_n, 0.0, 1.0);
    
    // To create a faint blur around the edges, increase the exponent value (1.8) to a larger number, such as 2.5 or 3.0.
    float edge_fade = pow(fresnel_edge, 3.0);

    vec3 cloud_color = vec3(0.9, 0.95, 1.0);

    // The value 0.75 at the end represents the maximum opacity at the densest part of the cloud.
    // If lower this value to 0.50 or 0.40, the cloud becomes more transparent.
    float final_alpha = cloud_mask * edge_fade * 0.8; 

    fragColor = vec4(cloud_color, final_alpha);
}