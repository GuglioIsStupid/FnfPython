import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene
import modules.Sprite as Sprite

import states.Playstate as Playstate

import modules.Wait as Wait

class TitleState(Scene.Base):
    def __init__(self):
        pg.mixer.music.load("assets/music/freakyMenu.ogg")

        self.danced = False
        self.gf = Sprite.Sprite(1280*0.4, 720*0.07)
        self.gf.setFrames(Sprite.getSparrow("menu/gfDanceTitle"))
        self.gf.addAnimByIndices("danceLeft", "gfDance", [30, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], 24, False)
        self.gf.addAnimByIndices("danceRight", "gfDance", [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29], 24, False)
        self.gf.play("danceLeft")

        self.logo = Sprite.Sprite(-150, -100)
        self.logo.setFrames(Sprite.getSparrow("menu/logoBumpin"))
        self.logo.addAnimByPrefix("bump", "logo bumpin", 24)
        self.logo.play("bump")

        self.enter = Sprite.Sprite(100, 720*0.8)
        self.enter.setFrames(Sprite.getSparrow("menu/titleEnter"))
        self.enter.addAnimByPrefix("idle", "Press Enter to Begin", 24, True)
        self.enter.addAnimByPrefix("press", "ENTER PRESSED", 24, True)
        self.enter.play("idle")

        pg.mixer.music.play(-1)

    def update(self, deltaTime):
        self.gf.update(deltaTime)
        self.logo.update(deltaTime)
        self.enter.update(deltaTime)

        # key presses
        pressed = pg.key.get_pressed()
        enter = pressed[K_RETURN] or pressed[K_KP_ENTER]

        if enter:
            self.enter.play("press")
            self.enter.offset = (-9, -5)
            # after 2 seconds, go to playstate (in a new thread)
            #threading.Timer(2, Scene.setScene, [Playstate.Playstate()]).start()
            #Wait.wait(2, lambda: Scene.setScene(Playstate.Playstate()))
            Scene.setScene(Playstate.Playstate())
            
    def render(self, screen):
        self.gf.draw(screen)
        self.logo.draw(screen)
        self.enter.draw(screen)

    def onBeat(self, beat):
        self.danced = not self.danced

        if self.danced:
            self.gf.play("danceRight")
        else:
            self.gf.play("danceLeft")

        self.logo.play("bump")

    def handle_events(self, events = None):
        pass

    def __unload__(self):
        #unload assets
        self.gf.unload()
        self.logo.unload()
        self.enter.unload()
        pass