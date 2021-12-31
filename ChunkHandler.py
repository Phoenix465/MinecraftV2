from random import randint

import glm
import numpy as np
from glm import vec3, ivec3

from Enumerations import *


class Chunk:
    def __init__(self, bottomLeft: vec3 = vec3()):
        self.bottomLeft = bottomLeft

        self.xSize = 16
        self.zSize = 16
        self.ySize = 256

        self.blockRelVec = [
            ivec3(0, -1, 0),
            ivec3(0, 1, 0),
            ivec3(1, 0, 0),
            ivec3(-1, 0, 0),
            ivec3(0, 0, -1),
            ivec3(0, 0, 1)
        ]

        print("Starting Chunk Generation", end=" ")

        # 2 Because it's Type, Face Mask
        self.ChunkData = np.empty((self.ySize, self.xSize, self.zSize, 2), dtype=np.uint8)
        for y in range(self.ySize):
            print(y, end=" ")
            for x in range(self.xSize):
                for z in range(self.zSize):
                    self.ChunkData[y, x, z, 0] = randint(1, 3)

                    # Storing Face Masks as single number using 6 bits
                    self.ChunkData[y, x, z, 1] = 0b00111111  # Bottom Top Right Left Front Back

        print("FINISHED")

    def UpdateFaceShow(self):
        print("Updating Faces           ", end=" ")
        for y, yData in enumerate(self.ChunkData):
            print(y, end=" ")
            for x, xData in enumerate(yData):
                for z, currentBlock in enumerate(xData):
                    currentVec = ivec3(x, y, z)
                    faceMask = 0
                    for i, relVec in enumerate(self.blockRelVec):
                        newVec = currentVec + relVec
                        if 0 <= newVec.x < self.xSize and 0 <= newVec.y < self.ySize and 0 <= newVec.z < self.zSize:
                            newBlock = self.ChunkData[newVec.y][newVec.x][newVec.z]

                            if newBlock[0]:
                                faceMask = faceMask << 1 | 0
                            else:
                                faceMask = faceMask << 1 | 1
                        else:
                            faceMask = faceMask << 1 | 1

                    currentBlock[1] = faceMask & 255

        print("FINISHED")
        np.save("test.npy", self.ChunkData)

    def serialize(self):
        print("Serializing", end=" ")
        tempData = [
            x | y << 4 | z << 4+8 | zData[0] << 4+8+4 | zData[1] << 4+8+4+7
            #(x, y, z, zData[0])

            for y, yData in enumerate(self.ChunkData)
            for x, xData in enumerate(yData)
            for z, zData in enumerate(xData)
            if zData[0] and zData[1]  # If Type != 0 AND FaceMask != 0b00_000000
        ]

        flatData = np.array(tempData, dtype=np.uint32).flatten()
        print("Finished")

        from sys import getsizeof
        print(getsizeof(flatData), getsizeof(self.ChunkData))
        return flatData, len(tempData)
