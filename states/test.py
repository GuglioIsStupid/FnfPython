import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene
import modules.Sprite as Sprite

class TestScene(Scene.Base):
    def __init__(self):
        self.timer = 0
        self.test = Sprite.Sprite(0, 0)
        self.test.setFrames(Sprite.getSparrow("todd"))
        self.test.addAnimByPrefix("idle", "idle", 24, True)
        self.test.play("idle")
        pass

    def update(self, deltaTime):
        self.timer += 25
        self.test.update(deltaTime)

    def render(self, screen):
        pg.draw.rect(screen,(255,0,0),(200,math.sin(self.timer)*50 + 50,100,50))
        self.test.draw(screen)

    def handle_events(self, events = None):
        pass