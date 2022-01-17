from __future__ import annotations

import ctypes
from time import perf_counter

import numpy as np
from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, glBufferData, \
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, \
    GL_STATIC_DRAW, GL_DYNAMIC_DRAW, \
    glVertexAttribPointer, glEnableVertexAttribArray, glVertexAttribDivisor, \
    glDrawElementsInstanced, glDrawElements, glDrawArrays, glGetAttribLocation, \
    GL_FLOAT, GL_INT, GL_FALSE, \
    GL_TRIANGLES, GL_LINES, GL_UNSIGNED_INT, glVertexAttribIPointer, glBufferSubData

import typing
from typing import Union

if typing.TYPE_CHECKING:
    from ChunkHandler import Chunk, Chunk2x2
    from UIHandler import Rectangle
    from DefaultBlockHandler import DefaultBlockFaceFill, DefaultBlockLines
    from BlockHandler import HighlightBlock


class VBOChunkBlock:
    def __init__(self,
                 shader,
                 defaultBlock: Union[DefaultBlockFaceFill, DefaultBlockLines],
                 mainObject: Union[Chunk, Chunk2x2, HighlightBlock],
                 isChunk=True):

        self.mainObject = mainObject
        self.drawMode = GL_TRIANGLES if isChunk else GL_LINES
        self.shader = shader

        self.vertices = np.array(defaultBlock.vertices, dtype=np.float32).flatten()
        self.indices = np.array(defaultBlock.indices, dtype=np.uint32).flatten()

        self.VAO = glGenVertexArrays(1)  # Vertex Array Object
        self.VBO = glGenBuffers(1)  # Vertex Buffer Object
        self.EBO = glGenBuffers(1)  # Element Buffer Object
        self.CBO = glGenBuffers(1)  # Chunk Buffer Object

        # Bind To Vertex Array Object
        glBindVertexArray(self.VAO)

        # Set Vertices in Block Template
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.vertices), self.vertices, GL_STATIC_DRAW)

        # Set Element Index in Block Template
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(self.indices), self.indices, GL_STATIC_DRAW)

        # Set Chunk Data
        chunkData, self.blockLength = self.mainObject.serialize(skip=True)

        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(chunkData), chunkData, GL_DYNAMIC_DRAW)

        templateStride = (3+1) * 4
        blockStride = (1+1) * 4

        self.vertexPositionLocation = glGetAttribLocation(shader, "vertexPosition")
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glVertexAttribPointer(self.vertexPositionLocation, 3, GL_FLOAT, GL_FALSE, templateStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.vertexPositionLocation)

        self.vertexFaceTypeLocation = glGetAttribLocation(shader, "vertexFaceType")
        glVertexAttribPointer(self.vertexFaceTypeLocation, 1, GL_FLOAT, GL_FALSE, templateStride, ctypes.c_void_p(3*4))
        glEnableVertexAttribArray(self.vertexFaceTypeLocation)

        self.packedDataLocation = glGetAttribLocation(shader, "packed_X_Y_Z_BlockId_FaceBitMaskId")
        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glVertexAttribIPointer(self.packedDataLocation, 1, GL_UNSIGNED_INT, blockStride, ctypes.c_void_p(0))
        glVertexAttribDivisor(self.packedDataLocation, 1)
        glEnableVertexAttribArray(self.packedDataLocation)

        self.chunkIdLocation = glGetAttribLocation(shader, "chunkId")
        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glVertexAttribIPointer(self.chunkIdLocation, 1, GL_UNSIGNED_INT, blockStride, ctypes.c_void_p(1*4))
        glVertexAttribDivisor(self.chunkIdLocation, 1)
        glEnableVertexAttribArray(self.chunkIdLocation)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.times = []

    def updateChunkBlockData(self):
        chunkBlockData, self.blockLength = self.mainObject.serialize()

        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(chunkBlockData), chunkBlockData, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self):
        s = perf_counter()
        glBindVertexArray(self.VAO)
        glDrawElementsInstanced(self.drawMode, len(self.indices), GL_UNSIGNED_INT, None, self.blockLength)
        glBindVertexArray(0)
        e = perf_counter() - s
        self.times.append(e*1000)
        self.times = self.times[:2000]


class VBORectangle:
    def __init__(self, shader, rectangle: Rectangle):
        self.shader = shader
        self.rectangle = rectangle

        self.vertices = self.rectangle.serialise()
        self.indices = np.array(self.rectangle.indices, dtype=np.uint32).flatten()

        self.VAO = glGenVertexArrays(1)  # Vertex Array Object
        self.VBO = glGenBuffers(1)  # Vertex Buffer Object
        self.EBO = glGenBuffers(1)  # Element Buffer Object

        glBindVertexArray(self.VAO)

        # Set Vertices in Block Template
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.vertices), self.vertices, GL_DYNAMIC_DRAW)

        # Set Element Index in Block Template
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(self.indices), self.indices, GL_STATIC_DRAW)

        vertexStride = (2+4)*4

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        self.positionLocation = glGetAttribLocation(shader, "position")
        glVertexAttribPointer(self.positionLocation, 2, GL_FLOAT, GL_FALSE, vertexStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.positionLocation)

        self.colourLocation = glGetAttribLocation(shader, "colour")
        glVertexAttribPointer(self.colourLocation, 4, GL_FLOAT, GL_FALSE, vertexStride, ctypes.c_void_p(2*4))
        glEnableVertexAttribArray(self.colourLocation)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def updateChunkData(self):
        newVertex = self.rectangle.serialise()

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(newVertex), newVertex, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
