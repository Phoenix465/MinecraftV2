from glm import vec3, length
from time import time

import ChunkHandler
import RayHandler
import TagHandler
import TweeningHandler


@TagHandler.ClassTag("PhysicsObjectAABB")
class PhysicsObjectAABB(object):
    def __init__(self, world=None, relativePositions=None, relativePositionPriority=None, gravityAffected=False, **kwargs):
        super(PhysicsObjectAABB, self).__init__(**kwargs)

        self.world = world
        self.relativePositions = relativePositions
        self.relativePositionPriority = relativePositionPriority
        self.gravityAffected = gravityAffected

        self.gravityVelocity = 0

        self.headPos = vec3(0, 0, 0)

        self.movementVector = vec3()
        self.movementTweenInfo = TweeningHandler.TweenInfo(time=1/20)

    def linkHeadPosToCamera(self, phyHeadPos):
        #  Ensuring Variable self.phyHeadPos is linked to phyHeadPos
        self.headPos = phyHeadPos

    @TagHandler.FunctionTag("physics-tick")
    def handleMovementAndCollision(self):
        movementVectorCopy = vec3(self.movementVector)
        self.movementVector = vec3(0, 0, 0)
        
        # Gravity
        if self.gravityAffected:
            self.gravityVelocity = (self.gravityVelocity - 0.08) * 0.98

        movementVectorCopy += vec3(0, self.gravityVelocity, 0)

        defaultBlock, closeChunks = RayHandler.DefaultBlockAABB(), ChunkHandler.GetCloseAdjacentChunks(self.world, self.headPos)

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

        if movementVectorCopy.z > movementVectorCopy.x:
            multipliers[1], multipliers[2] = multipliers[2], multipliers[1]
            inverse[1], inverse[2] = inverse[2], inverse[1]
            vectorIndexOrder[1], vectorIndexOrder[2] = vectorIndexOrder[2], vectorIndexOrder[1]

        phyHeadPosTemp = vec3(self.headPos)

        collisionIndex = [False, False, False]
        for vI, vMultiplier in enumerate(multipliers):
            movementDirection = movementVectorCopy * vMultiplier

            if length(movementDirection) == 0:
                continue

            moveRay = RayHandler.Ray(
                orig=phyHeadPosTemp,
                dir=movementDirection
            )

            didCollide = False
            distanceCollisions = []
            distanceI = []

            s = time()
            for i, relPos in enumerate(self.relativePositions):
                moveRay.orig = phyHeadPosTemp + relPos

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
                    if length(hitPos - moveRay.orig):
                        # True Correction
                        relBPos = moveRay.dir * -vec3(0.5, 1, 0.5)
                        hitPos = hitPos * inverse[vI] + (hitPosRoundV + relBPos) * multipliers[vI]

                    distanceCollisions.append(length(hitPos - moveRay.orig))
                    distanceI.append(i)

            e = time() - s

            if not didCollide:
                phyHeadPosTemp += movementDirection
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
                phyHeadPosTemp += moveRay.dir * max(minimumDistance - 0.001, 0)

                collisionIndex[vectorCheckIndex] = True

        if collisionIndex[1]:
            self.gravityVelocity = 0

        if self.headPos != phyHeadPosTemp:
            tween = TweeningHandler.Tween(self, self.movementTweenInfo, {"headPos": phyHeadPosTemp})
            tween.playT()

