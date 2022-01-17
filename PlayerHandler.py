from glm import vec3, vec2, ivec3

from BlockHandler import HighlightBlock
from CameraHandler import Camera


class Player(Camera):
    def __init__(self, shader, startPos: vec3, displayCentre: vec2, world):
        super().__init__(shader, startPos, displayCentre)
        self.world = world

    def GetCloseAdjacentChunks(self):
        returnChunks = []

        chunkDict = self.world.chunks
        chunkSizeVector = self.world.chunkSize * ivec3(1, 0, 1)

        closeChunkLeft = ivec3(self.headPos // self.world.chunkMultiplier * self.world.chunkMultiplier) * ivec3(1, 0, 1)

        for adjacentChunkCoords in self.world.chunkRelVec:
            chunkPos = closeChunkLeft + (adjacentChunkCoords * chunkSizeVector)

            if chunkPos in chunkDict:
                returnChunks.append(chunkDict[chunkPos])

        return returnChunks
