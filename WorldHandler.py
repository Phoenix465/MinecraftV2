from time import perf_counter

import numpy as np
from line_profiler_pycharm import profile
from opensimplex import OpenSimplex
from random import randint
from glm import vec3, ivec3
from ChunkHandler import Chunk, ChunkGroup, SerializeBlockData
from DefaultBlockHandler import DefaultBlockFaceFill
from OpenGL.GL import glUniform3f, glGetUniformLocation


class World:
    def __init__(self, shader):
        self.shader = shader

        self.noise = OpenSimplex(
            seed=123456#randint(10000, 99999)
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

    def setup(self):
        self.generateChunks()
        self.linkChunks()
        self.generateChunkBlocks()
        self.generateChunkGroups()
        self.updateChunkSurfaces()
        #self.updateChunkVBOs()
        self.updateChunkGroupsVBOs()

    def generateChunks(self):
        block = DefaultBlockFaceFill()

        s = perf_counter()

        size = 3
        chunkCounter = 0
        for chunkMultX in range(0, size):
            for chunkMultY in range(0, size):
                chunkCounter += 1

                print(f"\rCreating Chunks {chunkCounter:02} - {round((perf_counter() - s) * 1000, 1)}ms Elapsed", flush=True, end=" ")
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
            print(f"\rLinking Chunk {i+1} - {round((perf_counter()-s)*1000, 1)}ms Elapsed", flush=True, end=" ")

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
        for chunkGroup in self.chunkGroups.values():
            chunkGroup.VBO.updateChunkBlockData()

    def draw(self):
        s = perf_counter()
        for chunk in self.chunks.values():
            chunk.draw()
        e = perf_counter() - s

        self.times.append(e*1000)
        self.times = self.times[:600]

    def drawGroups(self):
        s = perf_counter()
        for chunkGroup in self.chunkGroups.values():
            chunkGroup.draw()
        e = perf_counter() - s

        self.times.append(e * 1000)
        self.times = self.times[:600]

    def removeBlock(self, chunkPos: ivec3, chunk):
        def GenerateDataAdjacentBlockRemoval(currentVec, chunk):
            updateData = []
            conversions = {
                0: 5 - 1,
                1: 5 - 0,
                2: 5 - 3,
                3: 5 - 2,
                4: 5 - 5,
                5: 5 - 4,
            }

            for i, relVec in enumerate(chunk.blockRelVec):
                newVec = currentVec + relVec

                if not 0 <= newVec.y < chunk.ySize:
                    continue

                if 0 <= newVec.x < chunk.xSize and 0 <= newVec.z < chunk.zSize:
                    newBlock = chunk.ChunkData[newVec.y, newVec.x, newVec.z]

                    if newBlock[0] != 0:
                        # Current Pos Chunk Id, old face, new face
                        adjI = conversions[i]
                        updateData.append(
                            (
                                newVec,
                                chunk.id,
                                newBlock[0],
                                newBlock[1],
                                ((newBlock[1] & ~(1 << adjI)) | (1 << adjI)) & 255,
                                chunk
                            )
                        )

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

                        if newBlock[0] != 0:
                            adjI = conversions[i]

                            updateData.append(
                                (
                                    newVec,
                                    adjChunk.id,
                                    newBlock[0],
                                    newBlock[1],
                                    ((newBlock[1] & ~(1 << adjI)) | (1 << adjI)) & 255,
                                    adjChunk
                                )
                            )

            return updateData

        chunkId = chunk.id
        blockData = chunk.ChunkData[chunkPos.y, chunkPos.x, chunkPos.z]
        blockId = SerializeBlockData(chunkPos, blockData)

        blockData[0] = 0
        blockData[1] = 0b000000

        chunkGroupObj = chunk.ChunkGroup

        if chunkGroupObj.serializeCache is None:
            return

        cache = chunkGroupObj.serializeCache

        filterMask = np.bitwise_and(
            cache[:, 0] == blockId,
            cache[:, 1] == chunkId
        )

        filterMask = np.invert(filterMask)
        filterArray = cache[filterMask]

        adjacentBlockRemovalData = GenerateDataAdjacentBlockRemoval(chunkPos, chunk)
        for (newChunkPos, newChunkId, newBlockId, oldFace, newFace, blockChunk) in adjacentBlockRemovalData:
            tempBlockId = SerializeBlockData(newChunkPos, (newBlockId, oldFace))
            newBlock = SerializeBlockData(newChunkPos, (newBlockId, newFace))

            if blockChunk not in chunkGroupObj.chunks:
                chunkGroupObj2 = blockChunk.ChunkGroup
                fArray = chunkGroupObj2.serializeCache

                if fArray is None:
                    continue

                mask = np.bitwise_and(
                    fArray[:, 0] == tempBlockId,
                    fArray[:, 1] == newChunkId
                )

                index = np.where(mask)[0]

                if len(index):
                    fArray[index, 0] = newBlock
                else:
                    fArray = np.append(fArray, [[newBlock, newChunkId]], axis=0)

                chunkGroupObj2.serializeCache = fArray
                chunkGroupObj2.VBO.updateChunkBlockData(useCache=True)

            else:
                mask = np.bitwise_and(
                    filterArray[:, 0] == tempBlockId,
                    filterArray[:, 1] == newChunkId
                )

                index = np.where(mask)[0]

                if len(index):
                    filterArray[index, 0] = newBlock
                else:
                    filterArray = np.append(filterArray, [[newBlock, newChunkId]], axis=0)

            blockChunk.ChunkData[newChunkPos.y, newChunkPos.x, newChunkPos.z, 1] = newFace

        chunkGroupObj.serializeCache = filterArray
        chunkGroupObj.VBO.updateChunkBlockData(useCache=True)
