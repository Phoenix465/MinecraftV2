#version 450 core
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;

uniform vec3 uniform_BlockTypeColours[128];

in vec3 vertexPosition;
in float vertexFaceType;
in uint packed_X_Y_Z_BlockId_FaceBitMaskId;

out vec4 fragColor;
out BLOCKVALIDITY {
    int valid;
} blockValidity;


void main()
{
    vec3 worldPosition = uvec3(
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x0000000F)) >> 0,
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x00000FF0)) >> 4,
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x0000F000)) >> 4+8
    );

    uint blockType = (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x007F0000)) >> 4+8+4;
    uint faceBitMaskId = (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x1F800000)) >> 4+8+4+7;

    vec4 rawPosition = uniform_Model * (vec4(worldPosition, 1) + (vec4(vertexPosition, 1)));
    gl_Position = uniform_Projection * uniform_View * rawPosition;

    vec3 colour = uniform_BlockTypeColours[blockType].xyz;
    uint vertexFaceTypeI = uint(vertexFaceType);

    blockValidity.valid = 1;

    if (((faceBitMaskId >> uint(5-vertexFaceTypeI)) & uint(0x1)) == 0)
    {
        blockValidity.valid = 0;
    }

    // if (vertexFaceTypeI == 0) { colour = vec3(1, 0, 0); }
    // if (vertexFaceTypeI == 1) { colour = vec3(1, 0, 0); }
    // if (vertexFaceTypeI == 2) { colour = vec3(0, 1, 0); }
    // if (vertexFaceTypeI == 3) { colour = vec3(0, 1, 0); }
    // if (vertexFaceTypeI == 4) { colour = vec3(0, 0, 1); }
    // if (vertexFaceTypeI == 5) { colour = vec3(0, 0, 1); }

    fragColor = vec4(colour, 1);
}