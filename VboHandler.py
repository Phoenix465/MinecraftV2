import ctypes
import numpy as np
from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, glBufferData, \
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, \
    GL_STATIC_DRAW, GL_DYNAMIC_DRAW, \
    glVertexAttribPointer, glEnableVertexAttribArray, glVertexAttribDivisor, \
    glDrawElementsInstanced, glGetAttribLocation, \
    GL_FLOAT, GL_INT, GL_FALSE, \
    GL_TRIANGLES, GL_UNSIGNED_INT, glVertexAttribIPointer

from ChunkHandler import Chunk
from DefaultBlockHandler import DefaultBlock


class VBOChunk:
    def __init__(self, shader, defaultBlock: DefaultBlock, chunkObject: Chunk):
        self.vertices = np.array(defaultBlock.vertices, dtype=np.float32).flatten()
        #self.normals = np.array(defaultBlock.normals, dtype=np.float32).flatten()
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
        chunkData, self.blockLength = chunkObject.serialize()

        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(chunkData), chunkData, GL_DYNAMIC_DRAW)

        templateStride = (3) * 4
        blockStride = (1) * 4

        self.vertexPositionLocation = glGetAttribLocation(shader, "vertexPosition")
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glVertexAttribPointer(self.vertexPositionLocation, 3, GL_FLOAT, GL_FALSE, templateStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.vertexPositionLocation)

        self.packedDataLocation = glGetAttribLocation(shader, "packed_X_Y_Z_BlockId_FaceBitMaskId")
        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glVertexAttribIPointer(self.packedDataLocation, 1, GL_UNSIGNED_INT, blockStride, ctypes.c_void_p(0))
        glVertexAttribDivisor(self.packedDataLocation, 1)
        glEnableVertexAttribArray(self.packedDataLocation)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawElementsInstanced(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None, self.blockLength)
        glBindVertexArray(0)