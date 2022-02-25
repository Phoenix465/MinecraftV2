import pygame
from time import time


class InputEvents:
    def __init__(self):
        self.quit = False
        self.MouseClickDown = [False, False, False]
        self.MouseClickUp = [False, False, False]
        self.MouseClickTiming = [None, None, None]

    def reset(self):
        self.MouseClickDown = [False, False, False]
        self.MouseClickUp = [False, False, False]

    def poll(self):
        self.reset()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True

            if event.type == pygame.MOUSEBUTTONDOWN and 1 <= event.button <= 3:
                self.MouseClickDown[event.button-1] = True
                self.MouseClickTiming[event.button-1] = time()

            elif event.type == pygame.MOUSEBUTTONUP and 1 <= event.button <= 3:
                self.MouseClickUp[event.button-1] = True
                self.MouseClickTiming[event.button-1] = None
