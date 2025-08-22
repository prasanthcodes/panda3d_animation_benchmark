//GLSL 
#version 150 compatibility

uniform sampler2D p3d_Texture0;
uniform struct PandaMaterial {
  vec4 ambient;
  vec4 diffuse;
  vec4 emission;
  vec3 specular;
  float shininess;
} p3d_Material;

uniform struct {
  vec4 ambient;
} p3d_LightModel;

uniform float has_fog = 0.0;

in vec3 mynormal;
in vec3 v;

#define MAX_LIGHTS 1 // to be modified when needed 

//https://en.wikibooks.org/wiki/GLSL_Programming/Blender/Diffuse_Reflection

void main() {
 
  vec3 texcolor = texture(p3d_Texture0, gl_TexCoord[0].st).rgb;
  vec3 EyeDir = normalize(-v); // we are in Eye Coordinates, so EyePos is (0,0,0)  
  float attenuation;

  //Lights   
  vec3 lightcolor = vec3(0.0,0.0,0.0);

  //Ambient
  lightcolor += vec3(p3d_LightModel.ambient * p3d_Material.ambient);

  //Emission
  lightcolor += vec3(p3d_Material.emission);

   for (int lm=0;lm<MAX_LIGHTS;lm++)
   {

      vec3 LightDir = vec3(0.0,0.0,0.0);

      if (0.0 == gl_LightSource[lm].position.w) // Directional light?
        {
         LightDir = normalize(vec3(gl_LightSource[lm].position.xyz));
		 attenuation = 1.0; // no attenuation with Dir Light
		}
     else // point or spot light?
	   {
	     LightDir = normalize( gl_LightSource[lm].position.xyz - v);
		 ///Diffuse and Specular Attenuation for point and spotlight
	     attenuation = 1.0 / (gl_LightSource[lm].constantAttenuation + gl_LightSource[lm].linearAttenuation * length(LightDir) + gl_LightSource[lm].quadraticAttenuation * length(LightDir) * length(LightDir));
	     if (gl_LightSource[lm].spotCutoff <= 90.0) // spotlight? 
               {
                  float clampedCosine = max(0.0, dot(-LightDir, gl_LightSource[lm].spotDirection));
                  if (clampedCosine < gl_LightSource[lm].spotCosCutoff) 
                     // outside of spotlight cone?
                  {
                     attenuation = 0.0;
                  }
                  else
                  {
                     attenuation = attenuation * pow(clampedCosine, gl_LightSource[lm].spotExponent);
                  }
               }
	     }
	    
      vec3 ReflectDir = normalize(-reflect(LightDir,mynormal));

	  //Diffuse
	  float NdotL = dot(normalize(mynormal),LightDir);
	  vec3 diffuseandspec = clamp(p3d_Material.diffuse.rgb * gl_LightSource[lm].diffuse.rgb * NdotL,0.0,1.0);
 
	  //Specular
	  vec4 specular = vec4(p3d_Material.specular, 1) * gl_LightSource[lm].specular * pow(max(dot(ReflectDir, EyeDir), 0), p3d_Material.shininess);
	  specular = clamp(specular, 0.0, 1.0); 
	  diffuseandspec  += specular.xyz;
   	  
	  diffuseandspec *= attenuation;
	  diffuseandspec = clamp(diffuseandspec, 0.0, 1.00); 
	  lightcolor += diffuseandspec;
	}

  //TexColor combined with LightColor
  texcolor *= lightcolor;

  //Fog (per Wezu's formula)
  float fogFactor = 1.0;
  if (has_fog == 1.0)
  {
  const float LOG2 = 1.442695;
  float z = gl_FragCoord.z / gl_FragCoord.w;
  fogFactor = exp2( -gl_Fog.density * gl_Fog.density * z * z * LOG2 );
  fogFactor = clamp(fogFactor, 0.0, 1.0);
  }
  
  //Final Color
  gl_FragColor = vec4(mix(gl_Fog.color.xyz,texcolor,fogFactor), 1.0); 
  
}