from time import time

import glm
from glm import vec3, vec2, ivec3, normalize, length, cross

import ChunkHandler
import RayHandler
from BlockHandler import HighlightBlock, ClosestFace, ClosestFaceSides
from CameraHandler import Camera
from DefaultBlockHandler import BlockSurfaceNullification
from InputHandler import InputEvents
from degreesMath import sin, cos


class Player(Camera):
    def __init__(self, shader, uiPlainShader, startPos: vec3, displayCentre: vec2, world, events: InputEvents):
        super().__init__(shader, uiPlainShader, startPos, displayCentre)

        self.world = world
        self.events = events

        self.cameraHeight = 1.5

        self.destroyHoldLastTime = time()
        self.destroyHoldTimeout = 0.6  # seconds
        self.destroyHoldDelay = 0.1
        
        self.addHoldLastTime = time()
        self.addHoldTimeout = 0.6   # seconds
        self.addHoldDelay = 0.1
        
        self.gravityVelocity = 0

        collisionRadius = 0.3
        self.relativePositions = [
            vec3(-collisionRadius, -self.cameraHeight, collisionRadius),  # 0
            vec3(collisionRadius, -self.cameraHeight, collisionRadius),  # 1
            vec3(collisionRadius, -self.cameraHeight, -collisionRadius),  # 2
            vec3(-collisionRadius, -self.cameraHeight, -collisionRadius),  # 3

            vec3(-collisionRadius, 0, collisionRadius),  # 4
            vec3(collisionRadius, 0, collisionRadius),  # 5
            vec3(collisionRadius, 0, -collisionRadius),  # 6
            vec3(-collisionRadius, 0, -collisionRadius),  # 7
        ]

        self.relativePositionPriority = {
            # Y: Up/Down
            (1, -1): [(0, 1, 2, 3), (4, 5, 6, 7)],
            (1, 1): [(4, 5, 6, 7), (0, 1, 2, 3)],

            # X: Right/Left
            (0, 1): [(1, 2, 5, 6), (0, 3, 4, 7)],
            (0, -1): [(0, 3, 4, 7), (1, 2, 5, 6)],

            # Z: Forward/Backwards (To You)
            (2, 1): [(0, 1, 4, 5), (2, 3, 6, 7)],
            (2, -1): [(2, 3, 6, 7), (0, 1, 4, 5)],
        }

        self.timeSinceGravityUpdate = time()

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
        movementVector = vec3(0, 0, 0)

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
                movementVector += moveDirections[i]

        # Gravity
        tick = 1/20
        if time() > self.timeSinceGravityUpdate + tick:
            self.timeSinceGravityUpdate = time()
            self.gravityVelocity = (self.gravityVelocity - 0.08) * 0.98
            print(self.gravityVelocity)
        movementVector += vec3(0, self.gravityVelocity * (dt / tick), 0)

        defaultBlock, closeChunks = RayHandler.DefaultBlockAABB(), self.GetCloseAdjacentChunks()

        multipliers = [
            vec3(0, 1, 0),
            vec3(0, 0, 1),
            vec3(1, 0, 0),
        ]
        inverse = [
            vec3(1, 0, 1),
            vec3(1, 1, 0),
            vec3(0, 1, 1),
        ]
        vectorIndexOrder = [
            1,  # Y
            2,  # Z
            0  # X
        ]

        if movementVector.z > movementVector.x:
            multipliers[1], multipliers[2] = multipliers[2], multipliers[1]
            inverse[1], inverse[2] = inverse[2], inverse[1]
            vectorIndexOrder[1], vectorIndexOrder[2] = vectorIndexOrder[2], vectorIndexOrder[1]

        collisionIndex = [False, False, False]
        for vI, vMultiplier in enumerate(multipliers):
            movementDirection = movementVector * vMultiplier

            if length(movementDirection) == 0:
                continue

            moveRay = RayHandler.Ray(
                orig=self.headPos,
                dir=movementDirection
            )

            didCollide = False
            distanceCollisions = []
            distanceI = []

            s = time()
            for i, relPos in enumerate(self.relativePositions):
                moveRay.orig = self.headPos + relPos

                hitPos, *_, hitPosRoundV = RayHandler.FindRayHitBlock(
                    moveRay,
                    defaultBlock,
                    closeChunks,
                    maxDist=abs(movementDirection[vectorIndexOrder[vI]]),
                    debug=False
                )

                if hitPos:
                    didCollide = True

                    # Not Instant Collide
                    if length(hitPos-moveRay.orig):
                        # True Correction
                        relBPos = moveRay.dir * -vec3(0.5, 1, 0.5)
                        hitPos = hitPos*inverse[vI] + (hitPosRoundV+relBPos)*multipliers[vI]

                    distanceCollisions.append(length(hitPos-moveRay.orig))
                    distanceI.append(i)

            e = time() - s

            if not didCollide:
                self.headPos += movementDirection
            else:
                vectorCheckIndex = vectorIndexOrder[vI]
                direction = round(moveRay.dir[vectorCheckIndex])

                priorityDistanceGroup = []
                priorityI = []
                for priorityGroup in self.relativePositionPriority[(vectorCheckIndex, direction)]:
                    foundRay = False
                    for rayIndex in priorityGroup:
                        if rayIndex in distanceI:
                            foundRay = True
                            priorityDistanceGroup.append(distanceCollisions[distanceI.index(rayIndex)])
                            priorityI.append(rayIndex)
                    if foundRay:
                        break

                minimumDistance = min(priorityDistanceGroup)
                searchIndex = priorityI[priorityDistanceGroup.index(minimumDistance)]
                # print(vI, searchIndex, priorityDistanceGroup, self.headPos - vec3(0, self.cameraHeight, 0))
                # self.headPos += movementDirection
                self.headPos += moveRay.dir * max(minimumDistance - 0.001, 0)
                # print(self.headPos, movementDirection, minimumDistance)

                collisionIndex[vectorCheckIndex] = True

        if collisionIndex[1]:
            self.gravityVelocity = 0
