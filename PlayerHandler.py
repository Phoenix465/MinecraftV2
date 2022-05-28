from time import time

import glm
from glm import vec3, vec2, ivec3, normalize, length, cross

import ChunkHandler
import RayHandler
from BlockHandler import HighlightBlock, ClosestFace, ClosestFaceSides
from CameraHandler import Camera
from DefaultBlockHandler import BlockSurfaceNullification
from PhysicsHandler import PhysicsObjectAABB
from InputHandler import InputEvents
from degreesMath import sin, cos


class Player(Camera, PhysicsObjectAABB):
    def __init__(self, shader, uiPlainShader, startPos: vec3, displayCentre: vec2, world, events: InputEvents):
        super(Player, self).__init__(
            shader=shader, uiPlainShader=uiPlainShader, startPos=startPos, displayCentre=displayCentre,
            world=world,
            relativePositions=[
                vec3(-0.3, -1.5, 0.3),  # 0
                vec3(0.3, -1.5, 0.3),  # 1
                vec3(0.3, -1.5, -0.3),  # 2
                vec3(-0.3, -1.5, -0.3),  # 3

                vec3(-0.3, 0, 0.3),  # 4
                vec3(0.3, 0, 0.3),  # 5
                vec3(0.3, 0, -0.3),  # 6
                vec3(-0.3, 0, -0.3),  # 7
            ],

            relativePositionPriority={
                # Y: Up/Down
                (1, -1): [(0, 1, 2, 3), (4, 5, 6, 7)],
                (1, 1): [(4, 5, 6, 7), (0, 1, 2, 3)],
                # X: Right/Left
                (0, 1): [(1, 2, 5, 6), (0, 3, 4, 7)],
                (0, -1): [(0, 3, 4, 7), (1, 2, 5, 6)],
                # Z: Forward/Backwards (To You)
                (2, 1): [(0, 1, 4, 5), (2, 3, 6, 7)],
                (2, -1): [(2, 3, 6, 7), (0, 1, 4, 5)],
            },

            gravityAffected=True
        )

        self.linkHeadPosToCamera(self.headPos)

        self.world = world
        self.events = events

        self.destroyHoldLastTime = time()
        self.destroyHoldTimeout = 0.6  # seconds
        self.destroyHoldDelay = 0.1

        self.addHoldLastTime = time()
        self.addHoldTimeout = 0.6  # seconds
        self.addHoldDelay = 0.1

    def mouseHandler(self):
        blockRemove = self.events.MouseClickDown[0]
        blockAdd = self.events.MouseClickDown[2]

        if self.events.MouseClickTiming[0] and self.events.MouseClickTiming[
            0] + self.destroyHoldTimeout < time() and self.destroyHoldLastTime + self.destroyHoldDelay < time():
            self.destroyHoldLastTime = time()
            blockRemove = True

        if self.events.MouseClickTiming[2] and self.events.MouseClickTiming[
            2] + self.addHoldTimeout < time() and self.addHoldLastTime + self.addHoldDelay < time():
            self.addHoldLastTime = time()
            blockAdd = True

        hitPos, chunkPos, chunk, hitPosRound, hitPosRoundV = RayHandler.FindRayHitBlock(
            RayHandler.Ray(
                self.headPos,
                self.lookRelPos
            ),
            RayHandler.DefaultBlockAABB(),
            ChunkHandler.GetCloseAdjacentChunks(self.world, self.headPos)
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
                        minC = vec3(newRealPos) - vec3(0.5, 0, 0.5)
                        maxC = vec3(newRealPos) + vec3(0.5, 1, 0.5)

                        pMin = self.headPos + self.relativePositions[3]
                        pMax = self.headPos + self.relativePositions[5]

                        # Find if Player will Collide with Block Placement
                        if glm.all(glm.lessThan(minC, pMax)) and glm.all(glm.greaterThan(maxC, pMin)):
                            break

                        addPos = newRealPos - chunk.bottomLeft
                        self.world.addBlock(addPos, chunk, 1)

                        break

        else:
            self.highlightBlock.show = False

    def movementHandler(self, dt):
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

        for i, keyMove in enumerate(self.events.WASDHold):
            if keyMove:
                self.movementVector += moveDirections[i]