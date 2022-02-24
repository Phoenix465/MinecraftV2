from glm import vec3, vec2, ivec3

import ChunkHandler
import RayHandler
from BlockHandler import HighlightBlock, ClosestFace
from CameraHandler import Camera
from InputHandler import InputEvents


class Player(Camera):
    def __init__(self, shader, startPos: vec3, displayCentre: vec2, world, events: InputEvents):
        super().__init__(shader, startPos, displayCentre)
        self.world = world
        self.events = events

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

    def mouseHandler(self):
        blockRemove = self.events.MouseClickDown[0]
        blockAdd = self.events.MouseClickDown[2]

        hitPos, chunkPos, chunk, hitPosRound, hitPosRoundV = RayHandler.FindRayHitBlock(
            RayHandler.Ray(
                self.headPos,
                self.lookRelPos
            ),
            RayHandler.DefaultBlockAABB(),
            self.GetCloseAdjacentChunks()
        )

        if hitPos:
            self.highlightBlock.chunkPos = chunkPos
            self.highlightBlock.chunkId = chunk.id
            self.highlightBlock.show = True
            self.highlightBlock.VBOBlock.updateChunkBlockData()

            if blockAdd:
                surfaceI = ClosestFace(hitPos - hitPosRoundV)
                newRealPos = hitPosRound + chunk.blockRelVec[surfaceI]

                for chunk in self.world.chunks.values():
                    if ChunkHandler.IsPointInChunkV(chunk, newRealPos):
                        addPos = newRealPos - chunk.bottomLeft
                        self.world.addBlock(addPos, chunk, 1)

                        break
            if blockRemove:
                self.world.removeBlock(chunkPos, chunk)

        else:
            self.highlightBlock.show = False
