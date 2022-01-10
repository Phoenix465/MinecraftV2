from OpenGL.GL import shaders
from OpenGL.GL import *

import pygame

import numpy as np


def run():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)  # Vertex Buffer Object

    glBindVertexArray(VAO)

    vertices = np.array([[0, 1, 0], [-1, -1, 0], [1, -1, 0]], dtype=np.float32).flatten()
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL_DYNAMIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    EBO = glGenBuffers(1)  # Element Buffer Object

    # Create the index buffer object
    indices = np.array([[0, 1, 2]], dtype=np.int32).flatten()

    # Set Element Index in Block Template
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # Now create the shaders
    VERTEX_SHADER = shaders.compileShader("""
    #version 330
    layout(location = 0) in vec3 position;
    void main()
    {
        gl_Position = vec4(position, 1);
    }
    """, GL_VERTEX_SHADER)

    FRAGMENT_SHADER = shaders.compileShader("""
    #version 330
    out vec4 outputColor;
    void main()
    {
        outputColor = vec4(1.0f, 1.0f, 0.0f, 1.0f);
    }
    """, GL_FRAGMENT_SHADER)

    shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

    # The draw loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)

        glBindVertexArray(VAO)
        #glDrawArrays(GL_TRIANGLES, 0, 3)  # This line does work too!
        glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None)  # This line does work too!

        glBindVertexArray(0)

        # Show the screen
        pygame.display.flip()


run()
