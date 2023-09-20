import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene

class Template(Scene.Base):
    def __init__(self):
        pass

    def update(self, deltaTime):
        pass

    def render(self, screen):
        pass

    def handle_events(self, events = None):
        pass