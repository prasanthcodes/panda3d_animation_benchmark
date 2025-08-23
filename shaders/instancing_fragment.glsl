#version 430

in vec2 texcoord;
in vec4 vertex_color;

uniform sampler2D p3d_TextureModulate;

uniform struct PandaMaterial {
    vec4 diffuse;
} p3d_Material;

out vec4 p3d_FragColor;

void main() {
    p3d_FragColor = clamp(vertex_color * p3d_Material.diffuse * texture(p3d_TextureModulate, texcoord), 0.0, 1.0);
}