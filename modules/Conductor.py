import pygame as pg
from pygame.locals import *

global time, beat, lastBeat, bpm, beatHit, step, lastStep, stepHit
time = 0
beat = 0
step = 0
lastBeat = 0
lastStep = 0
bpm = 100
beatHit = False
stepHit = False

crochet = (60 / bpm) * 1000
stepCrochet = crochet / 4

def reset():
    global time, beat, lastBeat, beatHit, step, lastStep, stepHit
    time = pg.mixer.music.get_pos()/1000
    beat = 0
    step = 0
    lastBeat = 0
    lastStep = 0
    beatHit = False
    stepHit = False

def update(deltaTime):
    global time, beat, lastBeat, beatHit, step, lastStep, stepHit
    time = pg.mixer.music.get_pos()/1000
    beat = time * bpm / 60
    # 1 step = 1/4 beat
    step = (time * bpm / 60) * 4
    beatHit = False
    stepHit = False

    if int(beat) != int(lastBeat):
        lastBeat = beat
        beatHit = True

    if int(step) != int(lastStep):
        lastStep = step
        stepHit = True

        
def getBeat():
    return beat

def getBeatHit():
    return beatHit
