#version 450 core
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;

uniform vec3 uniform_BlockTypeColours[128];
uniform vec3 uniform_ChunkIdOffsets[128];
uniform vec3 blockNormals[6] = vec3[6](vec3(0, -1, 0), vec3(0, 1, 0), vec3(1, 0, 0), vec3(-1, 0, 0), vec3(0, 0, -1), vec3(0, 0, 1));

in vec3 vertexPosition;
in float vertexFaceType;
in uint packed_X_Y_Z_BlockId_FaceBitMaskId;
in uint chunkId;

flat out BLOCKDATA {
    int valid;
} blockData;

out vec4 fragColor;
out vec4 fragPos;
flat out vec4 normal;
// ONLY SEND VEC4 OUT OF THE VERTEX SHADER, CANNOT USE VEC3< OTHERWISE NOTHING SHOWS UP

void main()
{
    vec3 chunkPostition = uniform_ChunkIdOffsets[chunkId];

    vec3 worldPosition = uvec3(
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x0000000F)) >> 0,
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x00000FF0)) >> 4,
        (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x0000F000)) >> 4+8
    );

    uint blockType = (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x007F0000)) >> 4+8+4;
    uint faceBitMaskId = (packed_X_Y_Z_BlockId_FaceBitMaskId & uint(0x1F800000)) >> 4+8+4+7;

    vec4 rawPosition = uniform_Model * (vec4(chunkPostition + worldPosition + vertexPosition, 1));
    gl_Position = uniform_Projection * uniform_View * rawPosition;
    fragPos = rawPosition;

    vec3 colour = uniform_BlockTypeColours[blockType].xyz;
    uint vertexFaceTypeI = uint(vertexFaceType);

    blockData.valid = 1;

    if (((faceBitMaskId >> uint(5-vertexFaceTypeI)) & uint(0x1)) == 0)
    {
        blockData.valid = 0;
    }

    // if (vertexFaceTypeI == 0) { colour = vec3(1, 0, 0); }
    // if (vertexFaceTypeI == 1) { colour = vec3(1, 0, 0); }
    // if (vertexFaceTypeI == 2) { colour = vec3(0, 1, 0); }
    // if (vertexFaceTypeI == 3) { colour = vec3(0, 1, 0); }
    // if (vertexFaceTypeI == 4) { colour = vec3(0, 0, 1); }
    // if (vertexFaceTypeI == 5) { colour = vec3(0, 0, 1); }

    //colour = vec3(1, 1, 1);
    fragColor = vec4(colour, 1);
    normal = vec4(blockNormals[vertexFaceTypeI], 1);
    //blockData.normal = vec3(0, 1, 1);
}