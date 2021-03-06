import numpy as np
from glm import vec2, vec4, vec3
from pygame.image import load

import texture
from VboHandler import VBORectangle, VBOImageRectangle


def generateVertices(anchorPoint: vec2, size: vec2, anchor: vec2 = vec2(0, 0)):
    bottomLeft = anchorPoint - (size * anchor)
    vertices = (
        bottomLeft,
        bottomLeft + vec2(size.x, 0),
        bottomLeft + vec2(size.x, size.y),
        bottomLeft + vec2(0, size.y),
    )

    return vertices


class Rectangle:
    def __init__(self, shader, anchorPoint: vec2, size: vec2, colour: vec4, anchor: vec2 = vec2(0, 0)):
        self.vertices = generateVertices(anchorPoint, size, anchor)
        self.colours = [colour] * len(self.vertices)
        self.indices = (0, 1, 2, 0, 3, 2)
        self.VBO = VBORectangle(shader, self)

    def serialise(self):
        return np.array([vertex.to_list() + colour.to_list() for vertex, colour in zip(self.vertices, self.colours)], dtype=np.float32).flatten()

    def draw(self):
        self.VBO.draw()


class ImageRectangle:
    def __init__(self, shader, anchorPoint: vec2, size: vec2, colour: vec4, texture, anchor: vec2 = vec2(0, 0)):
        self.vertices = generateVertices(anchorPoint, size, anchor)
        self.textureCorners = [vec2(0, 1), vec2(1, 1), vec2(1, 0), vec2(0, 0)]
        self.colours = [colour] * len(self.vertices)
        self.indices = (0, 1, 2, 0, 3, 2)
        self.VBO = VBOImageRectangle(shader, self, texture)

    def changeTexture(self, texture):
        self.VBO.texture = texture

    def serialise(self):
        return np.array([vertex.to_list() + colour.to_list() + texCoord.to_list() for vertex, colour, texCoord in zip(self.vertices, self.colours, self.textureCorners)], dtype=np.float32).flatten()

    def draw(self):
        self.VBO.draw()


class Crosshair:
    def __init__(self, shader, displayV: vec2):
        thickness = 2.5
        length = 10

        thicknessW = thickness / displayV.x
        thicknessH = thickness / displayV.y
        lengthW = length / displayV.x
        lengthH = length / displayV.y

        colour = vec4(1, 1, 1, 1)

        self.crosshairRectangles = [
            Rectangle(shader, vec2(0, 0), vec2(thicknessW*2, thicknessH*2), colour, anchor=vec2(0.5, 0.5)),

            Rectangle(shader, vec2(thicknessW, 0), vec2(lengthW, thicknessH*2), colour, anchor=vec2(0, 0.5)),
            Rectangle(shader, vec2(-thicknessW, 0), vec2(lengthW, thicknessH*2), colour, anchor=vec2(1, 0.5)),
            Rectangle(shader, vec2(0, thicknessH), vec2(thicknessW*2, lengthH), colour, anchor=vec2(0.5, 0)),
            Rectangle(shader, vec2(0, -thicknessH), vec2(thicknessW*2, lengthH), colour, anchor=vec2(0.5, 1)),
        ]

    def draw(self):
        for rectangle in self.crosshairRectangles:
            rectangle.draw()


class NumberShower:
    def __init__(self, shader, basePath, digitHeight, topLeftVector, displayV, maxDigitLength: int = 8, defaultNumber: str=None,
                 imageSpacingMultiplier=0.75, extraImagePaths=None):
        self.loadedNumberImages, imageLoadsPaths = texture.loadAnimation(basePath, returnImage=True)

        baseImage = load(imageLoadsPaths[0])

        self.currentNumberString = "0" * maxDigitLength

        self.imageSize = texture.GetImageScaleSize(baseImage, digitHeight, displayV)
        self.imageSpacing = self.imageSize * vec2(imageSpacingMultiplier, 1)

        self.digitQuads = []
        self.digitShowMask = [1] * maxDigitLength

        self.extraImagePath = extraImagePaths or {}
        self.extraImages = {}
        for key, path in self.extraImagePath.items():
            self.extraImages[key] = texture.loadTexture(path)

        for i in range(maxDigitLength):
            newNumberQuad = ImageRectangle(
                shader,
                topLeftVector + vec2(i*self.imageSpacing.x, 0),
                self.imageSize,
                vec4(1, 1, 1, 1),
                self.loadedNumberImages[i],
            )

            self.digitQuads.append(newNumberQuad)

        if defaultNumber:
            self.setNumber(defaultNumber)

    def setNumber(self, num: str):
        for i, char in enumerate(num):
            if char == "-":
                self.digitShowMask[i] = 0
            elif char in self.extraImages:
                self.digitShowMask[i] = 1
                self.digitQuads[i].changeTexture(self.extraImages[char])
            else:
                self.digitShowMask[i] = 1
                self.digitQuads[i].changeTexture(self.loadedNumberImages[int(char)])

    def draw(self):
        for i, quad in enumerate(self.digitQuads):
            if self.digitShowMask[i]:
                quad.draw()
