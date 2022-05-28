from enum import Enum, unique
from glm import vec3


@unique
class BlockType(Enum):
    AIR = 0
    DIRT = 1
    GRASS = 2
    STONE = 3

    HIGHLIGHT = 127


class BlockColour(Enum):
    AIR = vec3(135, 206, 235) / 255
    DIRT = vec3(146, 108, 77) / 255
    GRASS = vec3(82, 105, 53) / 255
    STONE = vec3(169, 163, 163) / 255

    HIGHLIGHT = vec3(0, 0, 0)


@unique
class EasingStyle(Enum):
    Linear = 0
    Sine = 1
    Back = 2
    Quad = 3
    Quart = 4
    Quint = 5
    Bounce = 6
    Elastic = 7
    Exponential = 8
    Circular = 9
    Cubic = 10


@unique
class EasingDirection(Enum):
    In = 0
    Out = 1
    InOut = 2

