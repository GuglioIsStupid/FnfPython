import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene
import modules.ui.Note as Note
import modules.Sprite as Sprite
import json

import time, math
import modules.Conductor as Conductor
import modules.Camera as Camera

import modules.CoolUtil as CoolUtil

def round(x):
    return math.floor(x + 0.5)

global notes, musicTime, speed, previousFrameTime
musicTime = 0
speed = 1
previousFrameTime = 0

class Playstate(Scene.Base):
    uiScreen = pg.Surface((1280, 720), pg.SRCALPHA)
    gameScreen = pg.Surface((1280, 720))
    strumlineNotes = []
    unspawnNotes = []
    notes = []
    sustainNotes = []
    stage = "stage"
    def __generateStaticArrows(self, player):
        for i in range(0, 4):
            babyArrow = Sprite.Sprite(0, 100)
            babyArrow.setFrames(Sprite.getSparrow("NOTE_assets"))
            babyArrow.scale = (0.7, 0.7)
            if i == 0:
                babyArrow.x += Note.Note.swagWidth * 0
                babyArrow.addAnimByPrefix("static", "arrow static instance 1")
                babyArrow.addAnimByPrefix("pressed", "left press", 24, False)
                babyArrow.addAnimByPrefix("confirm", "left confirm", 24, False)
            elif i == 1:
                babyArrow.x += Note.Note.swagWidth * 1
                babyArrow.addAnimByPrefix("static", "arrow static instance 2")
                babyArrow.addAnimByPrefix("pressed", "down press", 24, False)
                babyArrow.addAnimByPrefix("confirm", "down confirm", 24, False)
            elif i == 2: # why is up and right swapped? idk lmao
                babyArrow.x += Note.Note.swagWidth * 2
                babyArrow.addAnimByPrefix("static", "arrow static instance 4")
                babyArrow.addAnimByPrefix("pressed", "up press", 24, False)
                babyArrow.addAnimByPrefix("confirm", "up confirm", 24, False)
            elif i == 3:
                babyArrow.x += Note.Note.swagWidth * 3
                babyArrow.addAnimByPrefix("static", "arrow static instance 3")
                babyArrow.addAnimByPrefix("pressed", "right press", 24, False)
                babyArrow.addAnimByPrefix("confirm", "right confirm", 24, False)
                
            babyArrow.play("confirm")
            babyArrow.x += 75
            babyArrow.x += ((1280/1.75) * player)
            babyArrow.centerOrigin()
            self.strumlineNotes.append(babyArrow)
                
    def __generate_song(self, chart):
        global Inst, Voices
        songPath = "assets/songs/" + chart + "/"
        #chart = json.decode("assets/data/" + chart + "/" + chart + ".json").song
        chart = json.load(open("assets/data/songs/" + chart + "/" + chart + ".json", "r"))["song"]
        # load inst and voices audio
        pg.mixer.music.load(songPath + "Inst.ogg")
        Voices = pg.mixer.Sound(songPath + "Voices.ogg")
        global speed
        speed = chart["speed"]

        # if chart stage exists, set self.stage to it, else set to "stage"
        if "stage" in chart:
            self.stage = chart["stage"]
        else:
            self.stage = "stage"
        
        noteData = chart["notes"]

        for section in noteData:
            for songNotes in section["sectionNotes"]:
                daStrumTime = songNotes[0]
                daNoteData = songNotes[1] % 4

                gottaHitNote = section["mustHitSection"]

                if songNotes[1] > 3:
                    gottaHitNote = section["mustHitSection"]

                swagNote = Note.Note(daStrumTime, daNoteData)

                # add to notes
                swagNote.sustainLength = songNotes[2]
                if len(songNotes) >= 4:
                    swagNote.altNote = songNotes[3]
                #swagNote.mustPress = gottaHitNote

                self.unspawnNotes.append(swagNote)

                susLength = songNotes[2]
                if susLength > 0:
                    thing = int(71 / speed)
                    length = int(susLength)
                    for susNote in range(thing, length, thing-7):
                        oldNote = self.unspawnNotes[len(self.unspawnNotes) - 1]
                        sustainNote = Note.Note(daStrumTime + susNote, daNoteData, oldNote, True)
                        sustainNote.mustPress = gottaHitNote
                        self.unspawnNotes.append(sustainNote)

                        if sustainNote.mustPress:
                            sustainNote.x += 1280/1.75


                swagNote.mustPress = gottaHitNote

                if swagNote.mustPress:
                    swagNote.x += 1280/1.75
            
        # sort unspawnNotes by strumTime
        self.unspawnNotes.sort(key=lambda x: x.strumTime, reverse=False)
    def __init__(self):
        global Inst, Voices, stageData, camGame, camHUD
        self.__generate_song("bopeebo")

        camGame = Camera.BaseCamera()
        camHUD = Camera.BaseCamera()

        stageData = __import__("assets.data.stages." + self.stage, fromlist=["assets.data.stages"]).Stage(camGame)

        # play audio
        previousFrameTime = time.time()
        # play inst
        Inst = pg.mixer.music
        Inst.play()
        Voices.play()

        self.__generateStaticArrows(0)
        self.__generateStaticArrows(1)

        for note in self.strumlineNotes:
            note.centerOrigin() 

    def update(self, deltaTime):
        stageData.update(deltaTime)
        global musicTime
        musicTime = Inst.get_pos()

        while (len(self.unspawnNotes) and self.unspawnNotes[0] != None and self.unspawnNotes[0].strumTime - musicTime < 1800 / speed):
            dunceNote = self.unspawnNotes[0]
            if not dunceNote.isSustainNote:
                self.notes.append(dunceNote)
            else:
                self.sustainNotes.append(dunceNote)

            index = self.unspawnNotes.index(dunceNote)
            self.unspawnNotes.pop(index)

        for note in self.notes:
            noteStrumtime = note.strumTime
            note.y = (100 - (int(musicTime) - int(noteStrumtime)) * (0.45 * speed))
            note.update(deltaTime)

        for note in self.sustainNotes:
            noteStrumtime = note.strumTime
            note.y = (100 - (int(musicTime) - int(noteStrumtime)) * (0.45 * speed))
            note.update(deltaTime)

        if len(self.notes) > 0 and self.notes[0].y < 100:
            # is not a must press note?
            if not self.notes[0].mustPress:
                self.strumlineNotes[self.notes[0].noteData].play("confirm", True)
                self.strumlineNotes[self.notes[0].noteData].centerOrigin()
            else:
                self.strumlineNotes[self.notes[0].noteData + 4].play("confirm", True)
                self.strumlineNotes[self.notes[0].noteData + 4].centerOrigin()

            self.notes.pop(0)

        if len(self.sustainNotes) > 0 and self.sustainNotes[0].y < 100 + self.sustainNotes[0].getFrameHeight():
            if not self.sustainNotes[0].mustPress:
                self.strumlineNotes[self.sustainNotes[0].noteData].play("confirm", True)
                self.strumlineNotes[self.sustainNotes[0].noteData].centerOrigin()
            else:
                self.strumlineNotes[self.sustainNotes[0].noteData + 4].play("confirm", True)
                self.strumlineNotes[self.sustainNotes[0].noteData + 4].centerOrigin()
            self.sustainNotes.pop(0)

        # if strumlineNotes is not animating, set to static
        for note in self.strumlineNotes:
            if note.curAnim != None:
                if note.curAnim["name"] == "confirm" and note.animFinished:
                    note.play("static")
                    note.centerOrigin()

        for note in self.strumlineNotes:
            note.update(deltaTime)

        camHUD.zoom = CoolUtil.lerp(camHUD.defaultZoom, camHUD.zoom, CoolUtil.clamp(1 - (deltaTime * 3.125), 0, 1))

    def render(self, screen):
        # clear the uiScreen and gameScreen
        self.gameScreen.fill((0, 0, 0))
        self.uiScreen.fill((0, 0, 0, 0))
        self.uiScreen.set_alpha(255)
                
        stageData.draw(self.gameScreen)

        for note in self.sustainNotes:
            if note.y < 800:
                note.draw(self.uiScreen, note.getFrameWidth()/4.25+25)

        for note in self.strumlineNotes:
            note.draw(self.uiScreen, 25)
            
        for note in self.notes:
            if note.y < 800:
                note.draw(self.uiScreen, note.getFrameWidth()/4.25+25)

        screen.blit(pg.transform.scale(self.gameScreen, (1280, 720)), (0, 0))
        screen.blit(pg.transform.scale(self.uiScreen, (1280 * camHUD.zoom, 720 * camHUD.zoom)), (0, 0))
        
    def onBeat(self, beat):
        if beat % 4 == 0:
            camHUD.zoom += 0.015

    def handle_events(self, events = None):
        pass