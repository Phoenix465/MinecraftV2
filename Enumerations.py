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
