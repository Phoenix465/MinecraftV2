from time import perf_counter

import numpy as np
from line_profiler_pycharm import profile
from opensimplex import OpenSimplex
from random import randint
from glm import vec3, ivec3
from ChunkHandler import Chunk, ChunkGroup, SerializeBlockData, SerializeBlockDataU
from DefaultBlockHandler import DefaultBlockFaceFill
from OpenGL.GL import glUniform3f, glGetUniformLocation


class World:
    def __init__(self, shader):
        self.shader = shader

        self.noise = OpenSimplex(
            seed=123456  # randint(10000, 99999)
        )

        self.chunks = {}
        self.chunksIds = {}
        self.chunkGroups = {}

        self.chunkSize = ivec3(16, 256, 16)
        self.chunkMultiplier = vec3(16, 0, 16)
        self.times = []

        self.chunkRelVec = [
            ivec3(0, 0, 0),

            ivec3(0, 0, -1),
            ivec3(0, 0, 1),
            ivec3(-1, 0, 0),
            ivec3(1, 0, 0),

            ivec3(1, 0, 1),
            ivec3(1, 0, -1),
            ivec3(-1, 0, 1),
            ivec3(-1, 0, -1),
        ]

        self.FaceIdAdjustmentRemoval = [[0 for i2 in range(6)] for i in range(64)]
        self.FaceIdAdjustmentAddition = [[0 for i2 in range(6)] for i in range(64)]
        self.frames = 0

    def setup(self):
        self.precomputeValues()
        self.generateChunks()
        self.linkChunks()
        self.generateChunkBlocks()
        self.generateChunkGroups()
        self.updateChunkSurfaces()
        # self.updateChunkVBOs()
        self.updateChunkGroupsVBOs()

    def precomputeValues(self):
        # Given the Face ID and adjustment index, set it to 1
        for faceId in range(64):
            for i in range(6):
                self.FaceIdAdjustmentRemoval[faceId][i] = ((faceId & ~(1 << i)) | (1 << i)) & 255
                self.FaceIdAdjustmentAddition[faceId][i] = ((faceId & ~(1 << i)) | (0 << i)) & 255

    def generateChunks(self):
        block = DefaultBlockFaceFill()

        s = perf_counter()

        size = 1
        chunkCounter = 0
        for chunkMultX in range(0, size):
            for chunkMultY in range(0, size):
                chunkCounter += 1

                print(f"\rCreating Chunks {chunkCounter:02} - {round((perf_counter() - s) * 1000, 1)}ms Elapsed",
                      flush=True, end=" ")
                chunkPosition = self.chunkSize * ivec3(chunkMultX, 0, chunkMultY)

                chunkPosition *= ivec3(1, 0, 1)

                glUniform3f(
                    glGetUniformLocation(self.shader, f"uniform_ChunkIdOffsets[{chunkCounter}]"),
                    *chunkPosition.to_list()
                )

                newChunk = Chunk(self.shader,
                                 self.noise,
                                 block,
                                 bottomLeft=chunkPosition,
                                 chunkSize=self.chunkSize,
                                 id=chunkCounter
                                 )

                self.chunks[chunkPosition] = newChunk
                self.chunksIds[chunkCounter] = newChunk

        print("FINISHED")

    def generateChunkGroups(self):
        block = DefaultBlockFaceFill()

        chunkGroupSize = vec3(
            self.chunkMultiplier.x * 2,
            1,
            self.chunkMultiplier.z * 2
        )

        chunkGroups = {}
        for _, chunk in self.chunks.items():
            groupPos = ivec3(chunk.bottomLeftV // chunkGroupSize * self.chunkMultiplier)

            if groupPos not in chunkGroups:
                chunkGroups[groupPos] = []

            if chunk not in chunkGroups[groupPos]:
                chunkGroups[groupPos].append(chunk)

        for groupPos, chunksGroup in chunkGroups.items():
            group = ChunkGroup(
                self.shader,
                block,
                chunksGroup
            )

            for chunk in chunksGroup:
                chunk.ChunkGroup = group

            self.chunkGroups[groupPos] = group

    def linkChunks(self):
        s = perf_counter()

        for i, (chunkPos, chunk) in enumerate(self.chunks.items()):
            print(f"\rLinking Chunk {i + 1} - {round((perf_counter() - s) * 1000, 1)}ms Elapsed", flush=True, end=" ")

            chunkAdjLink = {}

            for chunkOffset in chunk.chunkRelVecLinks.keys():
                newChunkPos = chunkPos + (chunkOffset * self.chunkSize)

                chunkAdjLink[chunkOffset] = self.chunks.get(newChunkPos, None)

            chunk.chunkRelVecLinks = chunkAdjLink

        print("FINISHED")

    def generateChunkBlocks(self):
        for chunk in self.chunks.values():
            chunk.GenerateChunk()

    def updateChunkSurfaces(self):
        for chunk in self.chunks.values():
            chunk.UpdateFaceShow()

    def updateChunkVBOs(self):
        for chunk in self.chunks.values():
            chunk.VBO.updateChunkBlockData()

    def updateChunkGroupsVBOs(self):
        for i, chunkGroup in enumerate(self.chunkGroups.values()):
            s = perf_counter()
            chunkGroup.VBO.updateChunkBlockData()
            e = perf_counter() - s
            print(f"Serializing {i} Group Chunk", e*1000)

    def update(self, targetFPS=60):
        self.frames += 1

        if self.frames % (targetFPS//8) == 0:
            for chunkGroup in self.chunkGroups.values():
                if chunkGroup.requireUpdateChunks:
                    chunkGroup.VBO.updateChunkBlockData(requireUpdate=True)

                chunkGroup.requireUpdateChunks = False

    def draw(self):
        s = perf_counter()
        for chunk in self.chunks.values():
            chunk.draw()
        e = perf_counter() - s

        self.times.append(e * 1000)
        self.times = self.times[:600]

    def drawGroups(self):
        s = perf_counter()
        for chunkGroup in self.chunkGroups.values():
            chunkGroup.draw()
        e = perf_counter() - s

        self.times.append(e * 1000)
        self.times = self.times[:600]

    def removeBlock(self, chunkPos: ivec3, chunk):
        chunk.ChunkData[chunkPos.y, chunkPos.x, chunkPos.z] = 0, 0b000000

        chunk.ChunkGroup.requireUpdateChunks = True
        chunk.requireUpdate = True

        enumerationBlockVec = enumerate(chunk.blockRelVec)
        for i, relVec in enumerationBlockVec:
            newVec = chunkPos + relVec

            if not 0 <= newVec.y < chunk.ySize:
                continue

            if 0 <= newVec.x < chunk.xSize and 0 <= newVec.z < chunk.zSize:
                newBlock = chunk.ChunkData[newVec.y, newVec.x, newVec.z]
                # chunk.ChunkGroup.requireUpdateChunks = True  # redundent as already done
                if newBlock[0]:
                    newBlock[1] = self.FaceIdAdjustmentRemoval[newBlock[1]][5 - i ^ 1]

            else:
                chunkOffset = ivec3(
                    -1 if newVec.x < 0 else (1 if newVec.x >= chunk.xSize else 0),
                    0,
                    -1 if newVec.z < 0 else (1 if newVec.z >= chunk.zSize else 0)
                )

                adjChunk = chunk.chunkRelVecLinks[chunkOffset]

                if adjChunk:
                    newVec = newVec - ivec3(chunk.xSize * chunkOffset.x, 0, chunk.zSize * chunkOffset.z)
                    newBlock = adjChunk.ChunkData[newVec.y, newVec.x, newVec.z]

                    if newBlock[0]:
                        newBlock[1] = self.FaceIdAdjustmentRemoval[newBlock[1]][5 - i ^ 1]

                        adjChunk.ChunkGroup.requireUpdateChunks = True
                        adjChunk.requireUpdate = True

    def addBlock(self, chunkPos: ivec3, chunk, blockId):
        chunk.ChunkGroup.requireUpdateChunks = True
        chunk.requireUpdate = True

        enumerationBlockVec = enumerate(chunk.blockRelVec)
        faceId = 0

        for i, relVec in enumerationBlockVec:
            newVec = chunkPos + relVec

            if not 0 <= newVec.y < chunk.ySize:
                continue

            if 0 <= newVec.x < chunk.xSize and 0 <= newVec.z < chunk.zSize:
                newBlock = chunk.ChunkData[newVec.y, newVec.x, newVec.z]
                # chunk.ChunkGroup.requireUpdateChunks = True  # redundent as already done
                if newBlock[0]:
                    newBlock[1] = self.FaceIdAdjustmentAddition[newBlock[1]][5 - i ^ 1]

                faceId = (faceId << 1) | (newBlock[0] == 0)

            else:
                chunkOffset = ivec3(
                    -1 if newVec.x < 0 else (1 if newVec.x >= chunk.xSize else 0),
                    0,
                    -1 if newVec.z < 0 else (1 if newVec.z >= chunk.zSize else 0)
                )

                adjChunk = chunk.chunkRelVecLinks[chunkOffset]

                if adjChunk:
                    newVec = newVec - ivec3(chunk.xSize * chunkOffset.x, 0, chunk.zSize * chunkOffset.z)
                    newBlock = adjChunk.ChunkData[newVec.y, newVec.x, newVec.z]

                    if newBlock[0]:
                        newBlock[1] = self.FaceIdAdjustmentAddition[newBlock[1]][5 - i ^ 1]

                        adjChunk.ChunkGroup.requireUpdateChunks = True
                        adjChunk.requireUpdate = True

                    faceId = (faceId << 1) | (newBlock[0] == 0)
                else:
                    faceId = (faceId << 1) | 1

        chunk.ChunkData[chunkPos.y, chunkPos.x, chunkPos.z] = blockId, faceId
