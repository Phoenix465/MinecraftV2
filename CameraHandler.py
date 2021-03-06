"""
Handler for the Camera Class

Class
-----
Camera - This Class handles the Client's Camera
"""
from pygame import key, K_w, K_s, K_a, K_d, K_q, K_e

import UIHandler
from BlockHandler import HighlightBlock
from degreesMath import cos, sin
from math import radians

from pygame.mouse import set_pos, get_pos
from glm import vec3, vec2, mat4, rotate, translate, normalize, length


class Camera(object):
    def __init__(self, shader=None, uiPlainShader=None, startPos: vec3=None, displayCentre: vec2=None, **kwargs):
        super(Camera, self).__init__(**kwargs)
        self.headPos = startPos

        self.lookRelPos = vec3()
        self.upVector = vec3(0, 1, 0)

        self.rotX = 0
        self.rotY = 0

        self.lookAtMatrix = self.getLookAtMatrix()

        self.speed = 5
        self.sensitivity = 0.1

        self.highlightBlock = HighlightBlock(shader)
        self.crosshair = UIHandler.Crosshair(uiPlainShader, displayCentre*2)

        self.displayCentre = displayCentre
        self.displaySize = (displayCentre[0] * 2, displayCentre[1] * 2)

    def rotateCamera(self):
        currentMousePosition = vec2(*get_pos())
        set_pos(self.displayCentre.to_tuple())

        deltaVector = (currentMousePosition - self.displayCentre) * self.sensitivity

        self.rotY -= deltaVector.y
        self.rotX += deltaVector.x

        if self.rotX >= 360:
            self.rotX -= 360

        if self.rotY < -85:
            self.rotY = -85

        elif self.rotY > 80:
            self.rotY = 80

        self.lookRelPos = vec3(
            cos(self.rotY) * sin(self.rotX),
            sin(self.rotY),
            -cos(self.rotY) * cos(self.rotX),
        )
        #print("LookPos", self.lookRelPos, length(self.lookRelPos))

        #print(self.lookRelPos)

        self.lookAtMatrix = self.getLookAtMatrix()

    def moveCamera(self, dt):
        keysPressed = key.get_pressed()

        directionalXVector = vec3(
            sin(-self.rotX),
            0,
            cos(-self.rotX)
        )

        directionalZVector = vec3(
            sin(-self.rotX - 90),
            0,
            cos(-self.rotX - 90)
        )

        frameDistance = self.speed * dt
        directionalXVector = normalize(directionalXVector) * frameDistance
        directionalZVector = normalize(directionalZVector) * frameDistance

        if keysPressed[K_w]:
            self.headPos -= directionalXVector

        if keysPressed[K_s]:
            self.headPos += directionalXVector

        if keysPressed[K_a]:
            self.headPos += directionalZVector

        if keysPressed[K_d]:
            self.headPos -= directionalZVector

        if keysPressed[K_q]:
            self.headPos.y -= frameDistance

        if keysPressed[K_e]:
            self.headPos.y += frameDistance

    def getLookAtMatrix(self):
        viewMatrix = mat4()
        yRotationMat = rotate(viewMatrix, radians(-self.rotY), (1, 0, 0))
        xRotationMat = rotate(viewMatrix, radians(self.rotX), (0, 1, 0))
        translationMat = translate(viewMatrix, self.headPos * -1)

        return yRotationMat * xRotationMat * translationMat

        #return lookAt(self.headPos, self.headPos+self.lookRelPos, self.upVector)
    
    def draw(self):
        self.highlightBlock.draw()

    def drawCrosshair(self):
        self.crosshair.draw()
