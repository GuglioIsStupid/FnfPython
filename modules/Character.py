import modules.Stage as Stage
import modules.Sprite as Sprite
import modules.Camera as Camera
import modules.ui.Note as Note

import pygame as pg
from pygame.locals import *

import json

import modules.Conductor as Conductor

class Character(Sprite.Sprite):
    char = None
    isPlayer = False
    animOffsets = {}
    
    __reverseDraw = False

    singDuration = 4
    lastHit = 0
    lastSing = None
    staticHoldAnimation = False

    danceSpeed = 2
    danced = False # for danceLeft and danceRight

    icon = "daddy-dearest"

    cameraPositiuon = (0, 0)

    def __init__(self, x=0,y=0,char=None,isPlayer=False,girlfriend=False): #char is a json file holding the character data
        super().__init__(x, y)
        self.char = json.load(open(char, "r"))
        x += self.char["position"][0]
        y += self.char["position"][1]
        self.x = x
        self.y = y
        self.isPlayer = isPlayer
        self.animOffsets = {}

        self.setFrames(Sprite.getSparrow(self.char["image"]))

        self.scale = (self.char["scale"], self.char["scale"])

        if self.isPlayer != self.char["flip_x"]:
            self.__reverseDraw = True
        
        if self.isPlayer != self.char["flip_x"] and not girlfriend: self.flipX = not self.flipX

        for anim in self.char["animations"]:
            animname = anim["anim"]
            # if "singLEFT" then switch to "singRIGHT", same with right
            if self.flipX and animname.startswith("sing"):
                if animname.endswith("LEFT"):
                    animname = animname.replace("LEFT", "RIGHT")
                elif animname.endswith("RIGHT"):
                    animname = animname.replace("RIGHT", "LEFT")
            if len(anim["indices"]) == 0:
                self.addAnimByPrefix(animname, anim["name"], anim["fps"], anim["loop"])
            else:
                self.addAnimByIndices(animname, anim["name"], anim["indices"], anim["fps"], anim["loop"])
            self.addOffset(animname, anim["offsets"][0], anim["offsets"][1])

        self.singDuration = 4
        self.lastHit = 0
        self.lastSing = None
        self.staticHoldAnimation = False

        self.danceSpeed = "dance_speed" in self.char and self.char["dance_speed"] or 2
        self.singDuration = self.char["sing_duration"]
        self.danced = False # for danceLeft and danceRight

        self.icon = self.char["healthicon"]

        self.cameraPosition = (self.char["camera_position"][0], self.char["camera_position"][1])

        self.dance()
        self.finish()

    def update(self, deltaTime):
        if self.curAnim:
            if  self.animFinished and (self.inAnims((self.curAnim["name"] + "-loop"))):
                self.playAnim(self.curAnim["name"] + "-loop")

        super().update(deltaTime)

    def draw(self, screen):
        super().draw(screen)

    def beat(self, beat):
        if self.lastHit > 0:
            if self.lastHit + Conductor.stepCrochet * self.singDuration * 1.1 <= pg.mixer.music.get_pos():
                self.dance()
                self.lastHit = 0
        elif beat % self.danceSpeed == 0:
            self.dance(self.danceSpeed < 2)

    def playAnim(self, anim, force=False, frame=1):
        super().play(anim, force, frame)

        if anim in self.animOffsets:
            self.offset = self.animOffsets[anim]
        else:
            self.offset = (0, 0)

    def sing(self, dir, miss=False, hold=False):
        if not self.staticHoldAnimation or not hold or self.lastSing != dir or self.lastSing == None or self.lastMiss != miss or self.lastMiss == None:
            anim = "sing" + Note.Note.directions[dir].upper()
            if miss: anim += "miss"
            self.playAnim(anim, True)
            
            self.lastSing = dir
            self.lastMiss = miss
        
        self.lastHit = pg.mixer.music.get_pos()
        
    def dance(self, force=None):
        # does __animations exist?
        if self.animationsExist:
            self.lastSing = None
            #if "danceLeft" in self.__animations and "danceRight" in self.__animations:
            if self.inAnims("danceLeft", "danceRight"):
                self.danced = not self.danced

                if self.danced:
                    self.playAnim("danceRight", force)
                else:
                    self.playAnim("danceLeft", force)
            elif self.inAnims("idle"):
                self.playAnim("idle", force)

    def addOffset(self, anim, x=0,y=0):
        self.animOffsets[anim] = (-x, -y)


