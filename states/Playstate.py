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
import modules.Character as Character
import modules.HealthIcon as HealthIcon
import modules.CoolUtil as CoolUtil


def round(x):
    return math.floor(x + 0.5)

global notes, musicTime, speed, previousFrameTime
musicTime = 0
speed = 1
previousFrameTime = 0

class Playstate(Scene.Base):
    uiScreen = pg.Surface((1280, 720), pg.SRCALPHA)
    iconScreen = pg.Surface((1280, 720), pg.SRCALPHA)
    zoomDifference = 1
    gameScreen = pg.Surface((1280, 720))
    strumlineNotes = []
    playerSustains = []
    enemySustains = [] # so they arent in the same list, so it doesn't interfere with eachothers
    unspawnNotes = []
    notes = []
    sustainNotes = []
    stage = "stage"
    song = None
    health = 1
    iconScale = 1
    score = 0
    accuracy = 0.0
    misses = 0
    notesHit = 0
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
        self.song = chart
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
                    gottaHitNote = not gottaHitNote

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
        global Inst, Voices, stageData, camGame, camHUD, camFollow
        self.__generate_song("test")

        camGame = Camera.BaseCamera()
        camHUD = Camera.BaseCamera()
        camFollow = Camera.BaseCamera()

        stageData = __import__("assets.data.stages." + self.stage, fromlist=["assets.data.stages"]).Stage(camGame)
        
        camGame.defaultZoom = stageData.defaultZoom

        # Find difference between camGame.defaultZoom and 1
        # e.g. 0.8 is a 0.2 difference, then we add 1 to get 1.2
        self.zoomDifference = 1 + (1 - camGame.defaultZoom) + 0.15
        #print(self.zoomDifference)
        self.gameScreen = pg.Surface((1280 * self.zoomDifference, 720 * self.zoomDifference))

        self.__generateStaticArrows(0)
        self.__generateStaticArrows(1)

        for note in self.strumlineNotes:
            note.centerOrigin() 

        stageData.boyfriend = Character.Character(stageData.boyfriendPos[0], stageData.boyfriendPos[1], "assets/data/characters/" + self.song["player1"] + ".json", True)
        stageData.boyfriend.camera = camGame

        stageData.enemy = Character.Character(stageData.enemyPos[0], stageData.enemyPos[1], "assets/data/characters/" + self.song["player2"] + ".json", False)
        stageData.enemy.camera = camGame

        gf = "gf"
        if "player3" in self.song:
            gf = self.song["player3"]
        
        stageData.girlfriend = Character.Character(stageData.girlfriendPos[0], stageData.girlfriendPos[1], "assets/data/characters/" + gf + ".json", False, True)
        stageData.girlfriend.camera = camGame
        stageData.girlfriend.danceSpeed = 1

        self.health = 1

        self.iconP1 = HealthIcon.HealthIcon(stageData.boyfriend.icon, True)
        self.iconP1.camera = camHUD

        self.iconP2 = HealthIcon.HealthIcon(stageData.enemy.icon, False)
        self.iconP2.camera = camHUD
            
        # play audio
        previousFrameTime = time.time()
        # play inst
        Inst = pg.mixer.music
        Inst.play()
        Voices.play()

    def update(self, deltaTime):
        self.iconP1.update(deltaTime)
        self.iconP2.update(deltaTime)
        stageData.update(deltaTime)
        global musicTime
        musicTime = Inst.get_pos()

        while (len(self.unspawnNotes) and self.unspawnNotes[0] != None and self.unspawnNotes[0].strumTime - musicTime < 1800 / speed):
            dunceNote = self.unspawnNotes[0]
            if not dunceNote.isSustainNote:
                self.notes.append(dunceNote)
            else:
                if dunceNote.mustPress:
                    self.playerSustains.append(dunceNote)
                else:
                    self.enemySustains.append(dunceNote)

            index = self.unspawnNotes.index(dunceNote)
            self.unspawnNotes.pop(index)

        for note in self.notes:
            noteStrumtime = note.strumTime
            note.y = (100 - (int(musicTime) - int(noteStrumtime)) * (0.45 * speed))
            note.update(deltaTime)

        for note in self.playerSustains:
            noteStrumtime = note.strumTime
            note.y = (100 - (int(musicTime) - int(noteStrumtime)) * (0.45 * speed))
            note.update(deltaTime)

        for note in self.enemySustains:
            noteStrumtime = note.strumTime
            note.y = (100 - (int(musicTime) - int(noteStrumtime)) * (0.45 * speed))
            note.update(deltaTime)

        if len(self.notes) > 0 and self.notes[0].y < 115:
            # is not a must press note?
            if not self.notes[0].mustPress:
                stageData.enemy.sing(self.notes[0].noteData, False, False)
                self.strumlineNotes[self.notes[0].noteData].play("confirm", True)
                self.strumlineNotes[self.notes[0].noteData].centerOrigin()
            else:
                stageData.boyfriend.sing(self.notes[0].noteData, False, False)
                self.strumlineNotes[self.notes[0].noteData + 4].play("confirm", True)
                self.strumlineNotes[self.notes[0].noteData + 4].centerOrigin()
                self.health -= 0.015
                self.score += 350
                self.notesHit += 1

            self.notes.pop(0)

        if len(self.playerSustains) > 0 and self.playerSustains[0].y < 100 + self.playerSustains[0].getFrameHeight():
            stageData.boyfriend.sing(self.playerSustains[0].noteData, False, True)
            self.strumlineNotes[self.playerSustains[0].noteData + 4].play("confirm", True)
            self.strumlineNotes[self.playerSustains[0].noteData + 4].centerOrigin()
            self.playerSustains.pop(0)

        if len(self.enemySustains) > 0 and self.enemySustains[0].y < 100 + self.enemySustains[0].getFrameHeight():
            stageData.enemy.sing(self.enemySustains[0].noteData, False, True)
            self.strumlineNotes[self.enemySustains[0].noteData].play("confirm", True)
            self.strumlineNotes[self.enemySustains[0].noteData].centerOrigin()
            self.enemySustains.pop(0)

        # if strumlineNotes is not animating, set to static
        for note in self.strumlineNotes:
            if note.curAnim != None:
                if note.curAnim["name"] == "confirm" and note.animFinished:
                    note.play("static")
                    note.centerOrigin()

        for note in self.strumlineNotes:
            note.update(deltaTime)

        camHUD.zoom = CoolUtil.lerp(camHUD.defaultZoom, camHUD.zoom, CoolUtil.clamp(1 - (deltaTime * 3.125), 0, 1))
        camGame.zoom = CoolUtil.lerp(camGame.defaultZoom, camGame.zoom, CoolUtil.clamp(1 - (deltaTime * 3.125), 0, 1))

        self.iconScale = CoolUtil.lerp(1, self.iconScale, CoolUtil.clamp(1 - (deltaTime * 6.25), 0, 1))

        stageData.boyfriend.update(deltaTime)
        stageData.enemy.update(deltaTime)
        stageData.girlfriend.update(deltaTime)

        if self.health < 0:
            self.health = 0
        elif self.health > 2: # dead
            self.health = 2

        self.iconP1.swap((self.health > 1.8 and 0 or 1))
        self.iconP2.swap((self.health < 0.2 and 0 or 1))

        # lerp camera to boyfriend
        #camGame.x = CoolUtil.lerp(camGame.x, stageData.boyfriend.x + stageData.boyfriend.cameraPosition[0], CoolUtil.clamp(1 - (deltaTime * 3.125), 0, 1))
        #camGame.y = CoolUtil.lerp(camGame.y, stageData.boyfriend.y + stageData.boyfriend.cameraPosition[1], CoolUtil.clamp(1 - (deltaTime * 3.125), 0, 1))

        
        #camGame.x = midpoint[0] - 400 - (stageData.boyfriend.cameraPosition[0])
        #camGame.y = midpoint[1] - 100 + (stageData.boyfriend.cameraPosition[1])

        # determine accuracy based off score and notesHit, 100 accuracy is 350 * notesHit
        if self.notesHit > 0:
            self.accuracy = (self.score / (350 * self.notesHit)) * 100
        else:
            self.accuracy = 0

        if math.floor(int(Conductor.step/16)) in range(0, len(self.song["notes"])):
            mustHit = self.song["notes"][math.floor(int(Conductor.step/16))]["mustHitSection"]
            if mustHit:
                midpoint = stageData.boyfriend.getMidpoint()
                camFollow.x = midpoint[0] - 2700 - (stageData.boyfriend.cameraPosition[0])
                camFollow.y = midpoint[1] - 1825 + (stageData.boyfriend.cameraPosition[1])
            else:
                midpoint = stageData.enemy.getMidpoint()
                camFollow.x = midpoint[0] - 700 - (stageData.enemy.cameraPosition[0])
                camFollow.y = midpoint[1] - 550 + (stageData.enemy.cameraPosition[1])  

        camGame.x = CoolUtil.coolLerp(camGame.x, camFollow.x, 1.75, deltaTime)
        camGame.y = CoolUtil.coolLerp(camGame.y, camFollow.y, 1.75, deltaTime)

    def render(self, screen):
        # clear the uiScreen and gameScreen
        self.gameScreen.fill((0, 0, 0))
        self.uiScreen.fill((0, 0, 0, 0))
        self.uiScreen.set_alpha(255)
        self.iconScreen.fill((0, 0, 0, 0))
        self.iconScreen.set_alpha(255)
                
        stageData.draw(self.gameScreen)

        for note in self.playerSustains:
            if note.y < 800:
                note.draw(self.uiScreen, note.getFrameWidth()/4.25+25)

        for note in self.enemySustains:
            if note.y < 800:
                note.draw(self.uiScreen, note.getFrameWidth()/4.25+25)

        for note in self.strumlineNotes:
            note.draw(self.uiScreen, 25)
            
        for note in self.notes:
            if note.y < 800:
                note.draw(self.uiScreen, note.getFrameWidth()/4.25+25)

        # display a health bar to uiScreen (dead center, 0.1 from height), like 25px tall
        self.uiScreen.fill((0, 0, 0), (1280/2 - 400, 720 - 100, 800, 25))
        # now draw a green rectangle overtop of it, 6px smaller on each side
        self.uiScreen.fill((0, 255, 0), (1280/2 - 394, 720 - 94, 788, 13))
        self.uiScreen.fill((255, 0, 0), (1280/2 - 394, 720 - 94, (788/2) * self.health, 13))
        # draw icons x based off (788/2) * self.health
        self.iconP1.draw(self.iconScreen, 1280/2 - 394 + (788/2) * self.health + 50, 485)
        self.iconP2.draw(self.iconScreen, 1280/2 - 394 + (788/2) * self.health - 55, 485)

        uiText = pg.font.Font("assets/fonts/vcr.ttf", 20).render(
            "Score: " + str(self.score) + " | Accuracy: " + str(round(self.accuracy)) + "% | Misses: " + str(self.misses),
            False, (0, 0, 0)
        )
        uitext_rect = uiText.get_rect(center=(1280/2, 720 - 50))
        self.uiScreen.blit(uiText, uitext_rect)

        # Camera blits (I am so fucking sorry, it's just how pygame is.....)
        screen.blit(pg.transform.scale(self.gameScreen, (
            1280 * self.zoomDifference * camGame.zoom, 
            720 * self.zoomDifference * camGame.zoom
        )), (
            (1280-(1280 * self.zoomDifference * camGame.zoom))/2, 
            (720-(720 * self.zoomDifference * camGame.zoom))/2)
        )
        screen.blit(pg.transform.scale(self.uiScreen, (
            1280 * camHUD.zoom, 
            720 * camHUD.zoom
        )), (
            (1280-(1280 * camHUD.zoom))/2, 
            (720-(720 * camHUD.zoom))/2)
        )
        screen.blit(pg.transform.scale(self.iconScreen, (
            1280 * camHUD.zoom * self.iconScale, 
            720 * camHUD.zoom * self.iconScale
        )), (
            (1280-(1280 * camHUD.zoom * self.iconScale))/2, 
            (720-(720 * camHUD.zoom * self.iconScale))/2)
        )
        
    def onBeat(self, beat):
        stageData.boyfriend.beat(beat)
        stageData.enemy.beat(beat)
        stageData.girlfriend.beat(beat)
        if beat % 4 == 0:
            camHUD.zoom += 0.015
            camGame.zoom += 0.015

        self.iconScale = 1.05

        if self.song["song"] == "Bopeebo":
            if beat % 8 == 7:
                stageData.boyfriend.playAnim("hey")

    def handle_events(self, events = None):
        pass