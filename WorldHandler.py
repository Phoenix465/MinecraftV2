from time import time

from opensimplex import OpenSimplex
from random import randint
from glm import vec3, ivec3
from ChunkHandler import Chunk
from OpenGL.GL import glUniform3f, glGetUniformLocation


class World:
    def __init__(self, shader):
        self.shader = shader

        self.noise = OpenSimplex(
            seed=123456#randint(10000, 99999)
        )

        self.chunks = {}
        self.chunkSize = ivec3(16, 256, 16)
        self.times = []

    def setup(self):
        self.generateChunks()
        self.linkChunks()
        self.generateChunkBlocks()
        self.updateChunkSurfaces()
        self.updateChunkVBOs()

    def generateChunks(self):
        s = time()

        size = 2
        chunkCounter = 0
        for chunkMultX in range(-size, size+1):
            for chunkMultY in range(-size, size+1):
                chunkCounter += 1

                print(f"\rCreating Chunks {chunkCounter:02} - {round((time() - s) * 1000, 1)}ms Elapsed", flush=True, end=" ")
                chunkPosition = self.chunkSize * ivec3(chunkMultX, 0, chunkMultY)

                chunkPosition *= ivec3(1, 0, 1)
                glUniform3f(
                    glGetUniformLocation(self.shader, f"uniform_ChunkIdOffsets[{chunkCounter}]"),
                    *chunkPosition.to_list()
                )

                newChunk = Chunk(self.shader,
                                 self.noise,
                                 bottomLeft=chunkPosition,
                                 chunkSize=self.chunkSize,
                                 id=chunkCounter
                                 )

                self.chunks[chunkPosition] = newChunk

        print("FINISHED")

    def linkChunks(self):
        s = time()

        for i, (chunkPos, chunk) in enumerate(self.chunks.items()):
            print(f"\rLinking Chunk {i+1} - {round((time()-s)*1000, 1)}ms Elapsed", flush=True, end=" ")

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
            chunk.VBO.updateChunkData()

    def draw(self):
        s = time()
        for chunk in self.chunks.values():
            chunk.draw()
        e = time() - s

        self.times.append(e*1000)
        self.times = self.times[:600]
