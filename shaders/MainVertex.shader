#version 450 core
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;

uniform vec3 uniform_BlockTypeColours[128];
uniform vec3 uniform_ChunkIdOffsets[128];
uniform vec3 blockNormals[6] = vec3[6](vec3(0, -1, 0), vec3(0, 1, 0), vec3(1, 0, 0), vec3(-1, 0, 0), vec3(0, 0, -1), vec3(0, 0, 1));
uniform vec2 faceTextureOffsets[6][4] = vec2[6][4](
    vec2[4](vec2(1.0f, 1.0f), vec2(0.0f, 1.0f), vec2(0.0f, 0.0f), vec2(1.0f, 0.0f)),
    vec2[4](vec2(1.0f, 1.0f), vec2(0.0f, 1.0f), vec2(0.0f, 0.0f), vec2(1.0f, 0.0f)),
    vec2[4](vec2(1.0f, 1.0f), vec2(0.0f, 1.0f), vec2(0.0f, 0.0f), vec2(1.0f, 0.0f)),
    vec2[4](vec2(1.0f, 1.0f), vec2(0.0f, 1.0f), vec2(0.0f, 0.0f), vec2(1.0f, 0.0f)),
    vec2[4](vec2(1.0f, 1.0f), vec2(0.0f, 1.0f), vec2(0.0f, 0.0f), vec2(1.0f, 0.0f)),
    vec2[4](vec2(1.0f, 1.0f), vec2(0.0f, 1.0f), vec2(0.0f, 0.0f), vec2(1.0f, 0.0f))
);
uniform int maxBlocks;
uniform ivec2 blockAtlasSize;

in vec3 vertexPosition;
in float vertexFaceType;
in uint packed_X_Y_Z_BlockId_FaceBitMaskId;
in uint chunkId;

flat out BLOCKDATA {
    int valid;
} blockData;

out vec4 fragColor;
out vec4 fragPos;
out vec4 textureCoordsV4;
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
    uint vertexFaceTypeI = uint(vertexFaceType) / 4;
    uint vertexFaceIPart =  uint(vertexFaceType) - (vertexFaceTypeI*4);

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

    colour = vec3(1, 1, 1);
    fragColor = vec4(colour, 1);
    normal = vec4(blockNormals[vertexFaceTypeI], 1);

    vec2 textureOffset = faceTextureOffsets[vertexFaceTypeI][vertexFaceIPart];
    textureOffset *= vec2(1.0f/6.0f, 1.0f/float(maxBlocks));
    vec2 textureCoords = vec2((vertexFaceTypeI * 1.0f/6.0f) + textureOffset.x, 1 - blockType/float(maxBlocks) - textureOffset.y);

    if (vertexFaceIPart == 0 || vertexFaceIPart == 1) {
        textureCoords += vec2(0, 0.001f);
    } else {
        textureCoords -= vec2(0, 0.001f);
    }

    if (vertexFaceIPart == 0 || vertexFaceIPart == 3) {
        textureCoords -= vec2(0.001f, 0);
    } else {
        textureCoords += vec2(0.001f, 0);
    }

    textureCoordsV4 = vec4(textureCoords, 0, 0);
}