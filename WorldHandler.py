from time import perf_counter

from opensimplex import OpenSimplex
from random import randint
from glm import vec3, ivec3
from ChunkHandler import Chunk, ChunkGroup
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

        size = 1
        chunkCounter = 0
        for chunkMultX in range(-size, size+1):
            for chunkMultY in range(-size, size+1):
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

        groups = 4

        keys = sorted(list(self.chunksIds.keys()), key=lambda id: id)

        chunkGroup = []
        chunkKeys = []

        for i, key in enumerate(keys):
            if i % groups == 0 and len(chunkKeys):
                self.chunkGroups[min(chunkKeys)] = ChunkGroup(
                    self.shader,
                    block,
                    chunkGroup
                )

                chunkGroup = []
                chunkKeys = []

            chunkKeys.append(key)
            chunkGroup.append(self.chunksIds[key])

        if len(chunkKeys):
            self.chunkGroups[min(chunkKeys)] = ChunkGroup(
                self.shader,
                block,
                chunkGroup
            )

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
