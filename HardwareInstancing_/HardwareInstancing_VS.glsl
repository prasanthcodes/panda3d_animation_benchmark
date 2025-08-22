//GLSL 
#version 150 compatibility

const int num_instances = %i;
uniform mat4 p3d_ModelViewProjectionMatrix;  
in vec4 p3d_Vertex; 
in vec4 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 shader_transformmatrix[num_instances];

in vec3 p3d_Normal;
out vec3 mynormal;
out vec3 v;


void main() 
{
  mat4 transform =  transpose(shader_transformmatrix[gl_InstanceID]); //Transpose is required
  gl_Position = p3d_ModelViewProjectionMatrix * (p3d_Vertex * transform);
  v =  (p3d_ModelViewMatrix * (p3d_Vertex * transform)).xyz; // Convert the vertex in the View space with the instanciation matrix (transform)
  vec3 instanciednormal = (vec4(p3d_Normal,0.0) * transform).xyz;
  mynormal = normalize(gl_NormalMatrix * instanciednormal);
  gl_TexCoord[0] = p3d_MultiTexCoord0;
}

