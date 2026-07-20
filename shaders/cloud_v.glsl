#version 300 es

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec2 v_uv;
out vec3 v_normal;
out vec3 v_view_dir;


void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    v_uv = p3d_MultiTexCoord0;

    // Calculating Normals and Vertex Positions in Camera Space.
    v_normal = normalize(p3d_NormalMatrix * p3d_Normal);
    vec4 view_pos = p3d_ModelViewMatrix * p3d_Vertex;
    v_view_dir = normalize(-view_pos.xyz); 
}


