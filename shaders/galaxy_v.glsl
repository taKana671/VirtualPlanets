#version 300 es

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;

// uniform vec3 u_sun_3d_pos;
// out vec2 v_sun_pos_2d;

void main()
    {
        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

        // vec4 projected_sun = p3d_ModelViewProjectionMatrix * vec4(u_sun_3d_pos, 1.0);
        // vec2 v_sun_pos_2d = projected_sun.xy / projected_sun.w;
    }