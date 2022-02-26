import sys
from functools import lru_cache
from math import sqrt
from random import randint
from time import perf_counter

from sys import getsizeof

import glm
import numpy as np
from glm import vec3, ivec3
from line_profiler_pycharm import profile
from numba import jit

from DefaultBlockHandler import DefaultBlockFaceFill
from Enumerations import *

from VboHandler import VBOChunkBlock
np.set_printoptions(threshold=sys.maxsize)


class Chunk:
    def __init__(self, shader, noise, blockObject, bottomLeft: ivec3 = ivec3(), chunkSize: ivec3 = ivec3(16, 256, 16), id=0):
        self.ChunkGroup = None
        self.requireUpdate = False
        self.serializeCache = None
        self.logSerialize = True

        self.bottomLeft = bottomLeft
        self.bottomLeftV = vec3(bottomLeft)
        self.id = id
        self.noise = noise

        self.xSize, self.ySize, self.zSize = chunkSize.to_tuple()
        self.minPos = self.bottomLeftV - vec3(0.5, 0.5, 0.5)
        self.maxPos = self.bottomLeftV + vec3(self.xSize, self.ySize, self.zSize) + vec3(0.5, 0.5, 0.5)
        self.minPosI = self.bottomLeft
        self.maxPosI = self.bottomLeft + ivec3(self.xSize, self.ySize, self.zSize)

        self.blockRelVec = [
            ivec3(0, -1, 0),
            ivec3(0, 1, 0),
            ivec3(1, 0, 0),
            ivec3(-1, 0, 0),
            ivec3(0, 0, 1),
            ivec3(0, 0, -1)
        ]
        
        self.chunkRelVecLinks = {
            ivec3(0, 0, -1): None,
            ivec3(0, 0, 1): None,
            ivec3(-1, 0, 0): None,
            ivec3(1, 0, 0): None,

            ivec3(1, 0, 1): None,
            ivec3(1, 0, -1): None,
            ivec3(-1, 0, 1): None,
            ivec3(-1, 0, -1): None,
        }

        self.adjIInverse = [~(1 << i) & (2**6-1) for i in range(6)]
        # 2 Because it's Type, Face Mask
        self.ChunkData = np.zeros((self.ySize, self.xSize, self.zSize, 2), dtype=np.uint8)
        self.VBO = VBOChunkBlock(shader, blockObject, self)

        self.DrawBlockLength = 0
        self.scale = 1/200

    def GenerateChunk(self):
        s = perf_counter()

        rangeValues = [-sqrt(2) / 2, sqrt(2) / 2]
        noisePoints = np.zeros((self.xSize, self.ySize))
        for x in range(self.xSize):
            for z in range(self.zSize):
                noisePoints[x, z] = self.noise.noise2d(
                    x=(x+self.bottomLeft.x) * self.scale,
                    y=(z+self.bottomLeft.z) * self.scale
                ) + rangeValues[1]

        for y in range(self.ySize):
            print(f"\rStarting Chunk {self.id:02} Generation {y:03} - {round((perf_counter()-s)*1000, 1)}ms Elapsed", flush=True, end=" ")

            for x in range(self.xSize):
                for z in range(self.zSize):
                    maxSolidPoint = noisePoints[x][z]
                    maxSolidPoint *= 16
                    maxSolidPoint = int(maxSolidPoint)

                    blockType = 0
                    if y == maxSolidPoint:
                        blockType = 2
                    elif 0 < y < maxSolidPoint:
                        blockType = 1
                    elif y == 0:
                        blockType = 3

                    self.ChunkData[y, x, z, 0] = blockType

                    # Storing Face Masks as single number using 6 bits
                    self.ChunkData[y, x, z, 1] = 0b111111  # Bottom Top Right Left Front Back

        print("FINISHED")

    def UpdateFaceShow(self):
        s = perf_counter()
        for y in range(self.ySize):
            print(f"\rUpdating Chunk {self.id:02} Faces      {y:03} - {round((perf_counter()-s)*1000, 1)}ms Elapsed", flush=True, end=" ")

            for x in range(self.xSize):
                for z in range(self.zSize):
                    currentBlock = self.ChunkData[y, x, z]

                    if currentBlock[0] == 0:
                        faceMask = 0b000000
                        currentBlock[1] = faceMask & 255
                        continue

                    currentVec = ivec3(x, y, z)
                    faceMask = 0
                    for i, relVec in enumerate(self.blockRelVec):
                        newVec = currentVec + relVec

                        if not 0 <= newVec.y < self.ySize:
                            faceMask = faceMask << 1 | 1

                            continue

                        if 0 <= newVec.x < self.xSize and 0 <= newVec.z < self.zSize:
                            newBlock = self.ChunkData[newVec.y, newVec.x, newVec.z]
                            faceMask = faceMask << 1 | (newBlock[0] == 0)

                        else:
                            chunkOffset = ivec3(
                                -1 if newVec.x < 0 else (1 if newVec.x >= self.xSize else 0),
                                0,
                                -1 if newVec.z < 0 else (1 if newVec.z >= self.zSize else 0)
                            )

                            adjChunk = self.chunkRelVecLinks[chunkOffset]

                            if adjChunk:
                                block = adjChunk.ChunkData[newVec.y, newVec.x - self.xSize*chunkOffset.x, newVec.z - self.zSize*chunkOffset.z]
                                faceMask = faceMask << 1 | (block[0] == 0)
                            else:
                                faceMask = faceMask << 1 | 1

                    currentBlock[1] = faceMask & 255

        print("FINISHED")
        np.save("test.npy", self.ChunkData)

    def serialize(self, skip=False, useCache=False, requireUpdate=False):
        def serializeData(chunkData, id):
            #  x |
            #  y << 4 |
            #  z << 4 + 8 |
            #  zData[0] << 4 + 8 + 4 |
            #  zData[1] << 4 + 8 + 4 + 7
            #   = BlockId
            # ---- | -------- | ---- | ------- | ------
            #   X  |     Y    |  Z   |   Id    | FaceMask

            #  Only Pick Blocks With Id != 0 and Face Bit Mask != 0
            validBlocksMask = np.bitwise_and(chunkData[:, :, :, 0] > 0, chunkData[:, :, :, 1] > 0)

            #  Convert Block Mask To Index Positions in chunkData array and combine each 3 index to single array
            validBlockIndices = np.transpose(validBlocksMask.nonzero())

            # Convert Position Indices to a Position Id
            blockPositionIds = np.sum(np.left_shift(validBlockIndices, [4, 0, 4+8]), axis=1)

            # Convert Block Data to Block Ids
            blockDataIds = np.sum(np.left_shift(chunkData[validBlocksMask], [4+8+4, 4+8+4+7]), axis=1)

            # Sum Block and Position Ids
            blockIds = np.add(blockPositionIds, blockDataIds)

            # Recast from 64bit ints to 32bit ints
            blockIds = np.array(blockIds, dtype=np.uint32)

            # Add ID to every item in the list
            blockIds = np.insert(
                np.full(len(blockIds), id),
                np.arange(len(blockIds)), blockIds
            )

            return blockIds, len(blockIds)

        if skip:
            return np.array([]), 0

        if self.logSerialize:
            print(f"Serializing Chunk {self.id:02}", end=" ")
        s = perf_counter()

        serializedData, length = serializeData(self.ChunkData, self.id)
        self.serializeCache = serializedData
        self.DrawBlockLength = length

        e = perf_counter()
        if self.logSerialize:
            print("Finished", round((e-s)*1000, 3))
            self.logSerialize = False

        #print(getsizeof(serializedData), getsizeof(self.ChunkData), length)
        return serializedData, length

    def draw(self):
        self.VBO.draw()


class ChunkGroup:
    def __init__(self, shader, blockObject, chunks):
        self.chunks = chunks

        self.serializeCache = None
        self.VBO = VBOChunkBlock(shader, blockObject, self)
        self.requireUpdateChunks = False

    def serialize(self, skip=False, useCache=False, requireUpdate=False):
        if skip:
            return np.array([]), 0

        if useCache:
            blocks = self.serializeCache.ravel()
        else:
            blocks = np.concatenate([
                (chunk.serializeCache if requireUpdate and not chunk.requireUpdate else chunk.serialize()[0])
                for chunk in self.chunks
            ])
            self.serializeCache = blocks.reshape(len(blocks)//2, 2)

            if requireUpdate:
                for chunk in self.chunks:
                    chunk.requireUpdate = False

        return blocks, len(blocks)

    def draw(self):
        self.VBO.draw()


def IsPointInChunkI(chunk: Chunk, pos: ivec3):
    return glm.all(glm.greaterThanEqual(pos, chunk.minPosI)) and glm.all(glm.lessThan(pos, chunk.maxPosI))

def IsPointInChunkV(chunk: Chunk, pos: vec3):
    return glm.all(glm.greaterThanEqual(pos, chunk.minPos)) and glm.all(glm.lessThan(pos, chunk.maxPos))


@lru_cache(maxsize=None)
def SerializeBlockData(blockPos, blockData):
    return (
            (blockPos.x & 0b1111) |
            (blockPos.y & 0b11111111) << 4 |
            (blockPos.z & 0b1111) << 4 + 8 |
            (blockData[0] & 0b1111111) << 4 + 8 + 4 |
            (blockData[1] & 0b111111) << 4 + 8 + 4 + 7
    )


@lru_cache(maxsize=None)
def SerializeBlockDataU(blockPos, blockId, faceId):
    return (
            (blockPos.x & 0b1111) |
            (blockPos.y & 0b11111111) << 4 |
            (blockPos.z & 0b1111) << 4 + 8 |
            (blockId & 0b1111111) << 4 + 8 + 4 |
            (faceId & 0b111111) << 4 + 8 + 4 + 7
    )
