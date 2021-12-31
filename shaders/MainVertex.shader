#version 450 core
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;

uniform vec3 uniform_BlockTypeColours[128];

in vec3 vertexPosition;
in uint packed_X_Y_Z_BlockId_FaceBitMaskId;

out vec4 fragColor;

void main()
{
    vec3 worldPosition = uvec3(
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x00000F)) >> 0,
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x000FF0)) >> 4,
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x00F000)) >> 4+8
    );

    uint blockType = (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x7F0000)) >> 4+8+4;

    vec4 rawPosition = uniform_Model * (vec4(worldPosition, 1) + (vec4(vertexPosition, 1)));
    gl_Position = uniform_Projection * uniform_View * rawPosition;

    vec3 colour = uniform_BlockTypeColours[blockType].xyz;

    fragColor = vec4(colour, 1);
}