#version 330 core
out vec4 outputColor;

in vec4 FragColor;

void main()
{
    outputColor = FragColor;
}