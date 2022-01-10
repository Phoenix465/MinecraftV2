from degreesMath import sin, cos
from time import time

import glm
import pygame
from OpenGL.GL import *
from glm import vec3
from pygame import DOUBLEBUF, OPENGL
from pygame import GL_MULTISAMPLEBUFFERS, GL_MULTISAMPLESAMPLES

import CameraHandler
import GamePathHandler
import ShaderLoader
import ChunkHandler
import UIHandler
import WorldHandler
from Enumerations import *

import faulthandler


def main():
    # Initialisation
    pygame.init()
    GamePaths = GamePathHandler.PathHolder()

    # ----- Display Settings -----
    display = 1366, 768
    displayV = glm.vec2(display)

    #pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    #pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 2)

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Minecraft")
    pygame.mouse.set_visible(False)
    pygame.display.flip()

    # ----- Shader Settings -----
    shader = ShaderLoader.compileShaders(*GamePaths.defaultShaderPaths)
    uiPlainShader = ShaderLoader.compileShaders(*GamePaths.UIPlainShaderPaths)
    glUseProgram(shader)

    uniformModel = glGetUniformLocation(shader, 'uniform_Model')
    uniformView = glGetUniformLocation(shader, 'uniform_View')
    uniformProjection = glGetUniformLocation(shader, 'uniform_Projection')
    uniformLightPos = glGetUniformLocation(shader, 'uniform_LightPos')

    projectionMatrix = glm.perspective(70, displayV.x / displayV.y, 0.1, 1000.0)
    modelMatrix = glm.mat4(1)

    glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                       glm.value_ptr(modelMatrix))

    glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                       glm.value_ptr(projectionMatrix))

    blockExistCount = 0
    for blockType in BlockType:
        blockName, blockId = blockType.name, blockType.value
        blockColour = BlockColour[blockName].value
        blockExistCount += 1

        glUniform3f(glGetUniformLocation(shader, f'uniform_BlockTypeColours[{blockId}]'), *blockColour.to_tuple())

    # Sets all other block types to default white
    for extraId in range(blockExistCount, 128):
        glUniform3f(glGetUniformLocation(shader, f"uniform_BlockTypeColours[{extraId}]"), 1, 1, 1)

    # ----- OpenGL Settings -----
    version = GL_VERSION
    print(f"OpenGL Version: {glGetString(version).decode()}")

    glMatrixMode(GL_PROJECTION)
    # gluPerspective(70, (displayV.X / displayV.Y), 0.1, 128.0)
    glViewport(0, 0, int(displayV.x), int(displayV.y))
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glShadeModel(GL_FLAT)
    #glDisable(GL_CULL_FACE)
    #glCullFace(GL_FRONT_AND_BACK)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glClearColor(0.5294, 0.8078, 0.9216, 1.0)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # ----- Main ------
    times = [0]
    running = True
    clock = pygame.time.Clock()

    camera = CameraHandler.Camera(vec3(0, 5, 0), displayV/2)

    world = WorldHandler.World(shader)
    world.setup()

    crosshair = UIHandler.Crosshair(uiPlainShader, displayV)

    angle = 0
    radius = 5
    while running:
        deltaT = clock.tick(60) / 1000

        times = times[:600]
        angle += 5 * deltaT

        s = time() * 1000

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glUseProgram(shader)

        glUniformMatrix4fv(uniformView, 1, GL_FALSE,
                           glm.value_ptr(camera.lookAtMatrix))

        glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                           glm.value_ptr(modelMatrix))

        glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                           glm.value_ptr(projectionMatrix))

        glUniform3f(uniformLightPos, sin(angle)*radius, 16, cos(angle)*radius)

        camera.rotateCamera()
        camera.moveCamera(deltaT)

        world.draw()

        glUseProgram(uiPlainShader)
        crosshair.draw()

        pygame.display.flip()

        e = time() * 1000
        ft = e - s
        times.append(ft)

    print("Average ms Per Frame", sum(times) / len(times))
    print("Average ms Per Draw", sum(world.times) / len(world.times))


if __name__ == "__main__":
    """import cProfile, pstats

    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()"""
    faulthandler.enable()

    main()
