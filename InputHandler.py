import pygame
from time import time


class InputEvents:
    def __init__(self):
        self.quit = False

        self.MouseClickDown = [False, False, False]
        self.MouseClickUp = [False, False, False]
        self.MouseClickTiming = [None, None, None]

        self.WASD = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
        self.WASDHold = [False, False, False, False]

    def reset(self):
        self.MouseClickDown = [False, False, False]
        self.MouseClickUp = [False, False, False]

    def poll(self):
        self.reset()
        
        keysPressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True

            if event.type == pygame.MOUSEBUTTONDOWN and 1 <= event.button <= 3:
                self.MouseClickDown[event.button-1] = True
                self.MouseClickTiming[event.button-1] = time()

            elif event.type == pygame.MOUSEBUTTONUP and 1 <= event.button <= 3:
                self.MouseClickUp[event.button-1] = True
                self.MouseClickTiming[event.button-1] = None

        for i, key in enumerate(self.WASD):
            self.WASDHold[i] = keysPressed[key]
