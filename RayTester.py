from time import time

import pygame
from glm import vec3, vec2, normalize, length, silence
from math import isinf
from degreesMath import sin, cos
from line_profiler_pycharm import profile

silence(2)
display = 1366, 768
displayV = vec2(display)


class Box:
    def __init__(self, minV: vec3, maxV: vec3):
        self.bounds = [minV, maxV]

    def draw(self, window):
        points = [vec2(point.x, point.y) for point in self.bounds]
        points = [(point+1)/2 * displayV for point in points]

        rect = (points[0].to_list() + (points[1]-points[0]).to_list())
        pygame.draw.rect(window, (100, 200, 255), rect)


class Ray:
    def __init__(self, orig: vec3, dir: vec3):
        self.orig = orig
        self.dir = dir
        self.invdir = 1 / dir
        self.sign = [
            self.invdir.x < 0,
            self.invdir.y < 0,
            self.invdir.z < 0,
        ]

    def draw(self, window):
        scale = 0.1
        orig = (vec2(self.orig.x, self.orig.y) + 1) / 2 * displayV
        dir = (vec2(self.dir.x, self.dir.y)*scale) * displayV
        invdir = (vec2(self.invdir.x, self.invdir.y)*scale) * displayV

        pygame.draw.line(window, (100, 255, 100), orig, (orig[0]+dir[0], orig[1]+dir[1]), width=5)
        pygame.draw.line(window, (100, 100, 255), orig, (orig[0]+invdir[0], orig[1]+invdir[1]), width=5)

        pygame.draw.circle(window, (255, 0, 0), orig, 10)
        pygame.draw.circle(window, (100, 255, 100), orig + dir, 10)
        pygame.draw.circle(window, (100, 100, 255), orig + invdir, 10)


#@profile
def intersect(box: Box, ray: Ray):
    bounds = box.bounds

    tmin = (bounds[ray.sign[0]].x - ray.orig.x) * ray.invdir.x
    tmax = (bounds[1 - ray.sign[0]].x - ray.orig.x) * ray.invdir.x

    tymin = (bounds[ray.sign[1]].y - ray.orig.y) * ray.invdir.y
    tymax = (bounds[1 - ray.sign[1]].y - ray.orig.y) * ray.invdir.y

    tzmin = (bounds[ray.sign[2]].z - ray.orig.z) * ray.invdir.z
    tzmax = (bounds[1 - ray.sign[2]].z - ray.orig.z) * ray.invdir.z

    if tmin > tymax or tymin > tmax or tmin > tzmax or tzmin > tmax:
        return False, 0, 0

    tmax = min(tmax, tymax, tzmax)
    tmin = max(tmin, tymin, tzmin)

    tmin = 0 if isinf(tmin) else tmin
    tmax = 0 if isinf(tmax) else tmax

    return True, tmin, tmax


def main():
    pygame.init()

    screen = pygame.display.set_mode(display)
    pygame.display.set_caption("Ray Tester")
    pygame.display.flip()

    running = True

    background = (0, 0, 0)

    box = Box(vec3(-0.5, -0.5, 0), vec3(0.5, 0.5, 0))
    dir = vec3(0.5, 0.3, 0)
    ray = Ray(vec3(0, 0, 0), normalize(dir))

    angle = 0
    times = []

    while running:
        keyPressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print(f"{round(sum(times) / len(times), 4)}ms")
        scale = 0.002

        if keyPressed[pygame.K_w]:
            ray.__init__(ray.orig - vec3(0, scale, 0), ray.dir)
        if keyPressed[pygame.K_s]:
            ray.__init__(ray.orig - vec3(0, -scale, 0), ray.dir)
        if keyPressed[pygame.K_a]:
            ray.__init__(ray.orig - vec3(scale, 0, 0), ray.dir)
        if keyPressed[pygame.K_d]:
            ray.__init__(ray.orig - vec3(-scale, 0, 0), ray.dir)
        if keyPressed[pygame.K_q]:
            angle += 0.5
            ray.__init__(ray.orig, vec3(sin(angle), cos(angle), 0))
        if keyPressed[pygame.K_e]:
            angle -= 0.5
            ray.__init__(ray.orig, vec3(sin(angle), cos(angle), 0))
        screen.fill(background)

        s = time()
        collide, minDist, maxDist = intersect(box, ray)
        e = time() - s
        times.append(e*1000)
        if len(times) > 2500:
            del times[0]

        box.draw(screen)
        ray.draw(screen)

        if collide:
            pos = ray.orig + ray.dir*minDist
            pos2 = ray.orig + ray.dir*maxDist
            pos = (vec2(pos.x, pos.y) + 1) / 2 * displayV
            pos2 = (vec2(pos2.x, pos2.y) + 1) / 2 * displayV

            pygame.draw.circle(screen, (100, 100, 0), pos, 10)
            pygame.draw.circle(screen, (100, 0, 100), pos2, 10)

            orig = (vec2(ray.orig.x, ray.orig.y) + 1) / 2 * displayV
            pygame.draw.line(screen, (50, 255, 0), orig, pos, width=5)
            pygame.draw.line(screen, (50, 0, 255), orig, pos2, width=5)

        pygame.display.flip()


if __name__ == "__main__":
    main()

