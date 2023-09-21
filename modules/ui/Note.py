import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene

import xml.etree.ElementTree as ET

import modules.Path as Path

import modules.Sprite as Sprite

import modules.Conductor as Conductor

class Note(Sprite.Sprite):
    directions = ["left", "down", "up", "right"]
    strumTime = 0

    mustPress = False
    noteData = 0
    canBeHit = False
    tooLate = False
    wasGoodHit = False
    isEnd = False

    prevNote = None

    willMiss = False

    altNote = False
    invisNote = False

    sustainLength = 0
    isSustainNote = False

    noteScore = 1

    swagWidth = 160 * 0.7
    PURP_NOTE = 0
    BLUE_NOTE = 1
    GREEN_NOTE = 2
    RED_NOTE = 3

    arrowColors = [1,1,1,1]

    def __init__(self, strumTime, noteData, prevNote=None, sustainNote = False):
        super().__init__(0, 0)

        self.prevNote = prevNote != None and prevNote or self
        self.isSustainNote = sustainNote

        self.x += 75

        self.y -= 2000

        self.strumTime = strumTime
        self.noteData = noteData

        self.setFrames(Sprite.getSparrow("NOTE_assets"))
    
        self.addAnimByPrefix("greenScroll", "green instance")
        self.addAnimByPrefix("redScroll", "red instance")
        self.addAnimByPrefix("blueScroll", "blue instance")
        self.addAnimByPrefix("purpleScroll", "purple instance")

        self.addAnimByPrefix("purpleholdend", "pruple end hold")
        self.addAnimByPrefix("greenholdend", "green hold end")
        self.addAnimByPrefix("redholdend", "red hold end")
        self.addAnimByPrefix("blueholdend", "blue hold end")

        self.addAnimByPrefix("purplehold", "purple hold piece")
        self.addAnimByPrefix("greenhold", "green hold piece")
        self.addAnimByPrefix("redhold", "red hold piece")
        self.addAnimByPrefix("bluehold", "blue hold piece")

        self.scale = (0.7, 0.7)

        if noteData == 0:
            self.x += self.swagWidth * 0
            self.play("purpleScroll")
        elif noteData == 1:
            self.x += self.swagWidth * 1
            self.play("blueScroll")
        elif noteData == 2:
            self.x += self.swagWidth * 2
            self.play("greenScroll")
        elif noteData == 3:
            self.x += self.swagWidth * 3
            self.play("redScroll")

        if self.isSustainNote and self.prevNote != None:
            self.isSustainNote = True
            self.noteScore * 0.2
            self.alpha = 0.6
            self.isEnd = True

            self.x += self.width / 2

            if noteData == 0:
                self.play("purpleholdend")
            elif noteData == 1:
                self.play("blueholdend")
            elif noteData == 2:
                self.play("greenholdend")
            elif noteData == 3:
                self.play("redholdend")

            self.x -= self.width / 2
            if self.prevNote.isSustainNote:
                self.prevNote.isEnd = False
                if self.prevNote.noteData == 0:
                    self.prevNote.play("purplehold")
                elif self.prevNote.noteData == 1:
                    self.prevNote.play("bluehold")
                elif self.prevNote.noteData == 2:
                    self.prevNote.play("greenhold")
                elif self.prevNote.noteData == 3:
                    self.prevNote.play("redhold")

                self.offset = (0, 0)


        self.centerOrigin()

    def update(self, deltaTime):
        super().update(deltaTime)

        