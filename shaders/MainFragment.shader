#version 450 core

in vec4 fragColor;
in BLOCKVALIDITY {
    int valid;
} blockValidity;

layout (location = 0) out vec4 outColor;

void main()
{
    if (blockValidity.valid == 0)
    {
        discard;
    }

    outColor = fragColor;
}