# Libraries
import os, sys, random, time
import pygame as pg
from pygame.locals import *

global up, down, right, left
up = down = right = left = False

# Modules
import modules.state as Scene

# States
import states.test as test

pg.init()
 
fps = 60
clock = pg.time.Clock()
 
width, height = 640, 480
screen = pg.display.set_mode((width, height))

class MainLoop:
    def _update():
        Scene.curScene.handle_events(pg.event.get())
        Scene.curScene.update()
        
    def _draw():
        screen.fill((0,0,0))
        Scene.curScene.render(screen)
  
Scene.curScene = test.TestScene()
 
# Game loop.
while True:
    screen.fill((0, 0, 0))
  
    for event in pg.event.get():
        if event.type == QUIT: 
           raise SystemExit
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            raise SystemExit
        
        pressed = pg.key.get_pressed()
        left, down, up, right = [pressed[key] for key in (K_LEFT, K_DOWN, K_UP, K_RIGHT)]
  
    MainLoop._update()

    MainLoop._draw()
  
    pg.display.flip()
    clock.tick(fps)