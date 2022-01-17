from time import perf_counter

import numpy as np
from glm import ivec3

from DefaultBlockHandler import DefaultBlockLines
from VboHandler import VBOChunkBlock
from OpenGL.GL import glLineWidth


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

    def serialize(self, skip=False):
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
                pos.x |
                pos.y << 4 |
                pos.z << 4 + 8 |
                0b1111111 << 4 + 8 + 4 |
                0b111111 << 4 + 8 + 4 + 7,

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
