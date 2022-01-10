#version 450 core

uniform vec3 uniform_LightPos = vec3(0, 16, 0);
uniform vec3 uniform_LightColor = vec3(1, 1, 1);
uniform float uniform_AmbientStrength = 0.5;

in BLOCKDATA {
    int valid;
} blockData;
in vec4 fragColor;
in vec4 fragPos;
flat in vec4 normal;

out vec4 outColor;

void main()
{
    if (blockData.valid == 0)
    {
        discard;
    }

    vec3 ambient = uniform_AmbientStrength * uniform_LightColor;

    vec4 norm = vec4(normalize(normal.xyz), normal.w);
    vec3 lightDir = normalize(uniform_LightPos - fragPos.xyz);
    float diff = max(1.5*dot(norm.xyz, lightDir), 0.0);

    vec3 diffuse = diff * uniform_LightColor;
    vec3 result = (ambient + diffuse) * fragColor.xyz;
    outColor = vec4(result.xyz, 1);

}