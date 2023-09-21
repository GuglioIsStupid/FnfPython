# Libraries
import os, sys, random, time
import pygame as pg
from pygame.locals import *

global up, down, right, left
up = down = right = left = False

# Modules
import modules.state as Scene
import modules.Path as Path
import modules.Conductor as Conductor
import modules.Wait as Wait

# States
import states.test as test
import states.Playstate as Playstate
import states.TitleState as TitleState

pg.init()
 
fps = 165
clock = pg.time.Clock()
 
width, height = 1280, 720
global screen
screen = pg.display.set_mode((width, height))

pg.mixer.init()
pg.font.init()

global gameTime, lastTime, deltaTime
gameTime = time.time()
lastTime = time.time()
deltaTime = 0

class MainLoop:
    def _update(deltaTime):
        Scene.curScene.handle_events(pg.event.get())
        Scene.curScene.update(deltaTime)
        
    def _draw(screen):
        screen.fill((0,0,0))
        Scene.curScene.render(screen)
  
Scene.setScene(TitleState.TitleState())

font = pg.font.SysFont("Arial", 20)

pg.display.set_caption("Funkin' Python")
 
# Game loop.
while True:
    gameTime = time.time()
    deltaTime = gameTime - lastTime
    screen.fill((0, 0, 0))
  
    for event in pg.event.get():
        if event.type == QUIT: 
           raise SystemExit
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            raise SystemExit
        
        pressed = pg.key.get_pressed()
        left, down, up, right = [pressed[key] for key in (K_LEFT, K_DOWN, K_UP, K_RIGHT)]
        
    MainLoop._update(deltaTime)
    Conductor.update(deltaTime)

    Wait.update(deltaTime)

    if Conductor.getBeatHit():
        if Scene.curScene.onBeat != None: Scene.curScene.onBeat(int(Conductor.getBeat()))

    MainLoop._draw(screen)
    # update the screen
    # debug text on top left displaying fps
    screen.blit(font.render(str(int(clock.get_fps())), False, (255, 255, 255)), (0, 0))

    pg.display.flip()
    clock.tick(fps)
    lastTime = gameTime
    #print(clock.get_fps())
    pg.display.update()

    