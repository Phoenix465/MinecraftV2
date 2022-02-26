from math import floor
from typing import List

from glm import vec3, isinf, normalize, ivec3, length
from glm import round as glmRound
from line_profiler_pycharm import profile

from ChunkHandler import IsPointInChunkI


# Axis Aligned Bounding Box
class AABB:
    def __init__(self, minV: vec3, maxV: vec3):
        self.bounds = [minV, maxV]


class DefaultBlockAABB(AABB):
    def __init__(self):
        super().__init__(
            minV=vec3(-0.5, 0, -0.5),
            maxV=vec3(0.5, 1, 0.5),
        )



class Ray:
    def __init__(self, orig: vec3, dir: vec3):
        self.orig = vec3(orig)
        self.dir = normalize(dir)
        self.invdir = 1 / dir
        self.sign = [
            self.invdir.x < 0,
            self.invdir.y < 0,
            self.invdir.z < 0,
        ]


#@profile
def RayBoxIntersect(box: AABB, ray: Ray):
    bounds = box.bounds

    normBound = vec3(bounds[ray.sign[0]].x, bounds[ray.sign[1]].y, bounds[ray.sign[2]].z)
    invBound = vec3(bounds[1-ray.sign[0]].x, bounds[1-ray.sign[1]].y, bounds[1-ray.sign[2]].z)

    tmin, tymin, tzmin = (normBound - ray.orig) * ray.invdir
    tmax, tymax, tzmax = (invBound - ray.orig) * ray.invdir

    if tmin > tymax or tymin > tmax or tmin > tzmax or tzmin > tmax:
        return False, 0, 0

    tmax = min(tmax, tymax, tzmax)
    tmin = max(tmin, tymin, tzmin)

    tmin = 0 if isinf(tmin) else tmin
    tmax = 0 if isinf(tmax) else tmax

    return True, tmin, tmax


def FindRayHitBlock(ray: Ray, box: AABB, closeChunks, maxDist=10):
    #print("Init", ray.orig, ray.dir)
    origPos = ray.orig
    headPos = vec3(ray.orig)

    currentPos = ivec3(round(headPos.x), floor(headPos.y), round(headPos.z))
    currentPosV = vec3(currentPos)

    tempRay = Ray(ray.orig, ray.dir)

    while True:
        #print("Iteration")

        for chunk in closeChunks:
            if IsPointInChunkI(chunk, currentPos):
                chunkPos = currentPos - chunk.bottomLeft

                if not 0 <= chunkPos.y < chunk.ySize:
                    continue

                if chunk.ChunkData[chunkPos.y, chunkPos.x, chunkPos.z, 0]:
                    #print("SuccessfuSl")
                    return headPos, chunkPos, chunk, currentPos, currentPosV

                break

        relHeadPos = headPos - currentPosV
        tempRay.orig = relHeadPos

        collide, tmin, tmax = RayBoxIntersect(box, tempRay)
        
        if not collide:
            raise Exception("Collision Inside Box Not Detected")

        dirLength = tmin if tmin > 0 and tmin < tmax else (tmax if tmin < 0 and tmax > 0 else 0)
        #print(tempRay.orig, tmin, tmax)

        # Detect Ray Only Backwards
        if dirLength == 0:
            #print("Quit Early 2", tmin, tmax, tempRay.orig, tempRay.dir)
            return None, None, None, None, None

        if length(headPos - origPos) + dirLength > maxDist:
            #print("Quit Early")
            return None, None, None, None, None

        headPos = headPos + ray.dir*(dirLength+.00001)
        #print(headPos, length(headPos-origPos))

        currentPos = ivec3(round(headPos.x), floor(headPos.y), round(headPos.z))
        currentPosV = vec3(currentPos)
