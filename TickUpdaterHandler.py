from pygame.time import Clock
import threading
import TagHandler
import TweeningHandler
import queue


class TickUpdater:
    def __init__(self):
        self.ObjectCheck = []
        self.MainThreadFunctionsQueue = queue.Queue()

    def StartTickUpdater(self):
        target = 20

        def UpdateTick():
            def RunTagged(tagName):
                for obj in self.ObjectCheck:
                    if hasattr(obj, "_tagged"):
                        for function in obj.taggedFunctions:
                            if tagName in function._tags:
                                if "main-thread" in function._tags:
                                    self.MainThreadFunctionsQueue.put((function, obj))
                                else:
                                    function(obj)

            clock = Clock()

            while True:
                dt = clock.tick(target)

                RunTagged("physics-tick")
                RunTagged("world-chunk-update-tick")
                # self.ObjectCheck[0].update()

        updateThread = threading.Thread(target=UpdateTick, daemon=True)
        updateThread.start()
