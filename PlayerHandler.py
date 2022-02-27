from time import time

from glm import vec3, vec2, ivec3, normalize, length, cross

import ChunkHandler
import RayHandler
from BlockHandler import HighlightBlock, ClosestFace, ClosestFaceSides
from CameraHandler import Camera
from DefaultBlockHandler import MoveAlongBlock
from InputHandler import InputEvents
from degreesMath import sin, cos


class Player(Camera):
    def __init__(self, shader, uiPlainShader, startPos: vec3, displayCentre: vec2, world, events: InputEvents):
        super().__init__(shader, uiPlainShader, startPos, displayCentre)

        self.world = world
        self.events = events

        self.destroyHoldLastTime = time()
        self.destroyHoldTimeout = 1  # seconds
        self.destroyHoldDelay = 0.1
        
        self.addHoldLastTime = time()
        self.addHoldTimeout = 1  # seconds
        self.addHoldDelay = 0.1
        
        self.gravity = 9.8*2.9
        self.gravityVelocity = 0
        self.gravityMaxVelocity = 55.555
        self.gravityRay = RayHandler.Ray(self.headPos, vec3(0, -1, 0))

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

        if self.events.MouseClickTiming[0] and self.events.MouseClickTiming[0] + self.destroyHoldTimeout < time() and self.destroyHoldLastTime + self.destroyHoldDelay < time():
            self.destroyHoldLastTime = time()
            blockRemove = True

        if self.events.MouseClickTiming[2] and self.events.MouseClickTiming[2] + self.addHoldTimeout < time() and self.addHoldLastTime + self.addHoldDelay < time():
            self.addHoldLastTime = time()
            blockAdd = True

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

            if blockRemove:
                self.world.removeBlock(chunkPos, chunk)

            if blockAdd:
                surfaceI = ClosestFace(hitPos - hitPosRoundV)
                newRealPos = hitPosRound + chunk.blockRelVec[surfaceI]

                for chunk in self.world.chunks.values():
                    if ChunkHandler.IsPointInChunkI(chunk, newRealPos):
                        addPos = newRealPos - chunk.bottomLeft
                        self.world.addBlock(addPos, chunk, 1)

                        break

        else:
            self.highlightBlock.show = False

    def movementHandler(self, dt):
        # Gravity
        adjHead = self.headPos * vec3(1, 0, 1)
        currentChunk = None
        for chunk in self.world.chunks.values():
            if ChunkHandler.IsPointInChunkV(chunk, adjHead):
                currentChunk = chunk
                break

        if currentChunk:
            self.gravityRay.orig = self.headPos
            gravRange = 2
            hitPos, *_ = RayHandler.FindRayHitBlock(self.gravityRay, RayHandler.DefaultBlockAABB(), [currentChunk], maxDist=gravRange)

            if hitPos:
                self.headPos = hitPos + vec3(0, gravRange, 0)
                self.gravityVelocity = 0

            else:
                #adjGravity = ()
                self.gravityVelocity = max(-self.gravityMaxVelocity, self.gravityVelocity - self.gravity * dt)
                #self.gravityVelocity = self.gravityVelocity - self.gravity * dt

                #print(self.gravityVelocity, self.headPos.y)
                distance = self.gravityVelocity * dt
                self.headPos += vec3(0, distance, 0)

        # WASDKeys Movement
        directionalXVector = vec3(
            sin(-self.rotX),
            0,
            cos(-self.rotX)
        )

        directionalZVector = vec3(
            sin(-self.rotX - 90),
            0,
            cos(-self.rotX - 90)
        )

        frameDistance = self.speed * dt
        directionalNXVector = normalize(directionalXVector) * frameDistance
        directionalNZVector = normalize(directionalZVector) * frameDistance

        moveDirections = [-directionalNXVector, directionalNZVector, directionalNXVector, -directionalNZVector]
        resultantMove = vec3(0, 0, 0)

        for i, keyMove in enumerate(self.events.WASDHold):
            if keyMove:
                resultantMove += moveDirections[i]

        if not length(resultantMove) == 0:
            moveRay = RayHandler.Ray(
                self.headPos,
                resultantMove
            )

            thickness = 0.25
            perpendicularMove = normalize(cross(resultantMove, vec3(0, 1, 0)))

            rayPositions = [
                self.headPos,
                self.headPos +  perpendicularMove * thickness,
                self.headPos + -perpendicularMove * thickness
            ]
            rayHits = [None, None, None]
            rayHitsRoundV = [None, None, None]

            defaultBlock, closeChunks = RayHandler.DefaultBlockAABB(), self.GetCloseAdjacentChunks()

            for i, newHeadPos in enumerate(rayPositions):
                moveRay.orig = newHeadPos
    
                hitPos, *_, hitPosRoundV = RayHandler.FindRayHitBlock(
                    moveRay,
                    defaultBlock,
                    closeChunks,
                    maxDist=0.5
                )

                if hitPos:
                    rayHits[i] = hitPos
                    rayHitsRoundV[i] = hitPosRoundV

            if not any(rayHits):
                self.headPos += resultantMove
            else:
                if rayHits[0]:
                    targetPos = rayHits[0]
                    targetSurfaceI = ClosestFaceSides(targetPos - rayHitsRoundV[0])

                else:
                    newPos = self.headPos + resultantMove
                    distances = [(length(pos-newPos) if pos else 999) for pos in rayHits[1:]]

                    if min(distances) == 999:
                        return

                    pointIndex = 1+distances.index(min(distances))
                    targetPos = rayHits[pointIndex]
                    targetSurfaceI = ClosestFaceSides(targetPos - rayHitsRoundV[pointIndex])

                adjResultantNMove = MoveAlongBlock.moves[targetSurfaceI]
                possibleRelPos = [adjResultantNMove, -adjResultantNMove]
                possibleRelPosLengths = [length(relPos - resultantMove) for relPos in possibleRelPos]

                self.headPos += adjResultantNMove * length(resultantMove) * (
                    -1 if possibleRelPosLengths.index(min(possibleRelPosLengths)) else 1
                )
