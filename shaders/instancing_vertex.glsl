#version 430

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Color;

out vec2 texcoord;
out vec4 vertex_color;

struct Instanced {
    mat4 matrix;
};

layout(std430) buffer instanced_object {
    Instanced nodes[];
};

void main() {

    mat4 transform =  transpose(nodes[gl_InstanceID].matrix);
    vec4 vertex_position = p3d_Vertex * transform;
    vertex_color = p3d_Color;

    gl_Position = p3d_ModelViewProjectionMatrix * vertex_position;
    texcoord = p3d_MultiTexCoord0;

}