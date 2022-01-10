#version 450 core

in vec2 position;
in vec4 colour;

out vec4 FragColor;

void main()
{
    gl_Position = vec4(position, -0.0001f, 1.0);
    FragColor = colour;
}
