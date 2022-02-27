from time import perf_counter

import numpy as np
from glm import ivec3, vec3, length

from DefaultBlockHandler import DefaultBlockLines, CentreBlock
from VboHandler import VBOChunkBlock
from OpenGL.GL import glLineWidth
from ChunkHandler import SerializeBlockData


class HighlightBlock:
    def __init__(self, shader):
        self.chunkId = 0
        self.chunkPos = ivec3(0, 0, 0)
        self.show = False

        self.VBOBlock = VBOChunkBlock(
            shader,
            DefaultBlockLines(),
            self,
            isChunk=False
        )

    def draw(self):
        if self.show:
            glLineWidth(3)
            self.VBOBlock.draw()
            glLineWidth(1)

    def serialize(self, skip=False, useCache=False, requireUpdate=False):
        def serializeData(pos, id):
            #  x |
            #  y << 4 |
            #  z << 4 + 8 |
            #  zData[0] << 4 + 8 + 4 |
            #  zData[1] << 4 + 8 + 4 + 7
            #   = BlockId
            # ---- | -------- | ---- | ------- | ------
            #   X  |     Y    |  Z   |   Id    | FaceMask

            return np.array([
                SerializeBlockData(pos, (0b1111111, 0b111111)),
                id
            ], dtype=np.uint32), 1

        if skip:
            return np.array([]), 0

        #print(f"Serializing Highlight Block", end=" ")
        #s = perf_counter()

        serializedData, length = serializeData(self.chunkPos, self.chunkId)

        #e = perf_counter()
        #print("Finished", round((e-s)*1000, 3))

        #print(getsizeof(serializedData), getsizeof(self.ChunkData), length)
        return serializedData, length


def ClosestFace(point: vec3):
    distanceD = {length(point - centre): i for i, centre in enumerate(CentreBlock.centres)}
    minDist = min(distanceD.keys())

    return distanceD[minDist]


def ClosestFaceSides(point: vec3):
    distanceD = {length(point - centre): i for i, centre in enumerate(CentreBlock.centres) if i >= 2}
    minDist = min(distanceD.keys())

    return distanceD[minDist]