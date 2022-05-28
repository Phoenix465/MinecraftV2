import threading

from glm import vec3

from Enumerations import EasingStyle, EasingDirection
from time import time, sleep
from pygame.time import Clock


class TweenInfo:
    def __init__(self,
                 time: float = 1,
                 style: EasingStyle = EasingStyle.Linear,
                 direction: EasingDirection = EasingDirection.In,
                 repeat: int = -1,
                 reverses: bool = False,
                 delay: float = 0):

        self.time = time
        # self.style = style
        # self.direction = direction
        # self.repeat = repeat
        # self.reverses = reverses
        # self.delay = delay


class Tween:
    def __init__(self, obj, info: TweenInfo, propertyChange: dict):
        self.obj = obj
        self.info = info
        self.propertyChange = propertyChange

        if not hasattr(self.obj, "animationId"):
            self.obj.animationId = 0

    def play(self):
        def move(animationProgress, init, diff):
            for name in init.keys():
                setattr(self.obj, name, init[name] + (diff[name]*animationProgress))

        self.obj.animationId += 1
        currentId = self.obj.animationId

        initProperty = {name: getattr(self.obj, name) for name in self.propertyChange.keys() if hasattr(self.obj, name)}
        diffProperty = {name: self.propertyChange[name]-initProperty[name] for name in self.propertyChange.keys()}

        start = time()
        clock = Clock()
        while start + self.info.time > time():
            progress = min(1., (time()-start) / self.info.time)
            move(progress, initProperty, diffProperty)
            clock.tick(240)

            if currentId != self.obj.animationId:
                break

    def playT(self):
        thread = threading.Thread(target=self.play)
        thread.start()
