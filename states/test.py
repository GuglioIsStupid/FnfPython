import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene

class TestScene(Scene.Base):
    def __init__(self):
        self.timer = 0
        pass

    def update(self):
        self.timer += 25

    def render(self, screen):
        pg.draw.rect(screen,(255,0,0),(200,math.sin(self.timer)*50 + 50,100,50))

    def handle_events(self, events = None):
        pass