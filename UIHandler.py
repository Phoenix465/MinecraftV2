import numpy as np
from glm import vec2, vec4, vec3
from VboHandler import VBORectangle

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


class Crosshair:
    def __init__(self, shader, displayV: vec2):
        thickness = 2.5
        length = 10

        thicknessW = thickness / displayV.x
        thicknessH = thickness / displayV.y
        lengthW = length / displayV.x
        lengthH = length / displayV.y

        colour = vec4(1, 1, 1, 0.5)

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
