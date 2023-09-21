import pygame as pg
from pygame.locals import *
import math

import modules.state as Scene

import xml.etree.ElementTree as ET

import modules.Path as Path

def getSparrow(key):
    imgPath, xmlPath = "assets/images/" + key + ".png", "assets/images/" + key + ".xml"
    #img = pg.image.load(imgPath).convert_alpha()
    if not imgPath in Cache:
        Cache[imgPath] = pg.image.load(imgPath).convert_alpha()
    img = Cache[imgPath]
    obj = Sprite._getFramesFromSparrow(img, xmlPath)

    return obj

Cache = {}

def getImage(path):
    if not path in Cache:
        Cache[path] = pg.image.load(path).convert_alpha()
    return Cache[path]

class Sprite():
    def _newFrame(name, x, y, w, h, sw, sh, ox=None, oy=None, ow=None, oh=None):
        aw, ah = x + w, y + h
        frame = {}
        frame["name"] = name
        frame["quad"] = pg.Rect(x, y, aw > sw and w - (aw - sw) or w, ah > sh and h - (ah - sh) or h)
        frame["width"] = ow == None and w or ow
        frame["height"] = oh == None and h or oh
        frame["offset"] = (ox == None and 0 or ox, oy == None and 0 or oy)

        return frame

    def _getFramesFromSparrow(img, sparrow):
        sparrow = ET.parse(sparrow)
        # if img is a string, load it
        if type(img) == str:
            if not img in Cache:
                Cache[img] = pg.image.load(img).convert_alpha()

            img = Cache[img]

        frames = {"texture": img, "frames": []}
        sw, sh = img.get_size()
        for c in sparrow.findall("SubTexture"):
            frames["frames"].append(Sprite._newFrame(
                c.attrib["name"],
                int(c.attrib["x"]),
                int(c.attrib["y"]),
                int(c.attrib["width"]),
                int(c.attrib["height"]),
                sw,
                sh,
                int(c.attrib["frameX"] if "frameX" in c.attrib else 0),
                int(c.attrib["frameY"] if "frameY" in c.attrib else 0),
                int(c.attrib["frameWidth"] if "frameWidth" in c.attrib else 0),
                int(c.attrib["frameHeight"] if "frameHeight" in c.attrib else 0)
            )) 
            

        return frames

    def __init__(self, x, y, img = None):
        if x == None: x = 0
        if y == None: y = 0
        self.x = x
        self.y = y

        self.img = None
        self.width, self.height = 0, 0
        self.antialiasing = True

        self.camera = None
        
        self.alive = True
        self.exists = True

        self.origin = (0, 0)
        self.offset = (0, 0)
        self.scale = (1, 1)
        self.lastScale = (1, 1)
        self.scrollFactor = (1, 1)

        self.clipRect = None
        self.flipX = False
        self.flipY = False
        self.lastFlipX = False
        self.lastFlipY = False

        self.visible = True
        self.color = (255, 255, 255)
        self.alpha = 1
        self.lastAngle = 0
        self.angle = 0

        self.__frames = None
        self.__animations = None

        self.curAnim = None
        self.curFrame = None
        self.animFinished = None
        self.animPaused = False

        self.animationsExist = False

        if img != None: self._load(img)

    def _load(self, img, animated = None, framewidth = None, frameheight = None):
        if animated == None: animated = False

        if type(img) == str:
            if not img in Cache:
                Cache[img] = pg.image.load(img).convert_alpha()
            
            self.texture = Cache[img]
        
        self.curAnim = None
        self.curFrame = None
        self.animFinished = None

        if framewidth == None: framewidth = 0
        if frameheight == None: frameheight = 0

        if framewidth == 0:
            framewidth = animated and self.texture.get_rect().size[0] or self.texture.get_rect().size[0]
            framewidth = framewidth > self.texture.get_width() and self.texture.get_width() or framewidth

        self.width = framewidth

        if frameheight == 0:
            frameheight = animated and framewidth or self.texture.get_height()
            frameheight = frameheight > self.texture.get_height() and self.texture.get_height() or frameheight
        
        self.height = frameheight

        if animated:
            pass

    def setFrames(self, frames):
        self.__frames = frames
        self.texture = frames["texture"]

        self._load(self.texture)
        self.width, self.height = self.texture.get_size()

    def updateHitbox(self):
        w, h = self.getFrameWidth(), self.getFrameHeight()

        self.width = abs(self.scale[0]) * w
        self.height = abs(self.scale[1]) * h

        self.offset = (-0.5 * (self.width - w), -0.5 * (self.height - h))
        self.centerOrigin()

    def centerOrigin(self):
        self.origin = (self.getFrameWidth() * 0.5, self.getFrameHeight() * 0.5)

    def addAnimByPrefix(self, name, prefix, framerate = None, looped = None):
        if self.__animations == None: self.__animations = {}
        self.animationsExist = True
        if framerate == None: framerate = 30
        if looped == None: looped = True

        anim = {}
        anim["name"] = name
        anim["framerate"] = framerate
        anim["looped"] = looped
        anim["frames"] = []

        for frame in self.__frames["frames"]:
            if frame["name"].startswith(prefix):
                anim["frames"].append(frame)

        self.__animations[name] = anim

    def addAnimByIndices(self, name, prefix, indices, framerate = None, looped = None):
        if self.__animations == None: self.__animations = {}
        self.animationsExist = True
        if framerate == None: framerate = 30
        if looped == None: looped = True

        anim = {}
        anim["name"] = name
        anim["framerate"] = framerate
        anim["looped"] = looped
        anim["frames"] = []

        # only take the last 3 characters of the prefix
        subEnd = len(prefix)
        for i in indices:
            for f in self.__frames["frames"]:
                #print(f["name"].startswith(prefix) and f["name"][subEnd:])
                if f["name"].startswith(prefix) and int(f["name"][subEnd:]) == i:
                    anim["frames"].append(f)
                    break


        self.__animations[name] = anim

    # multiple arguments, inAnims
    def inAnims(self, *args):
        for arg in args:
            if not arg in self.__animations:
                return False
        return True

    def getCurrentFrame(self):
        if self.curAnim:
            if math.floor(self.curFrame) - 1 in range(len(self.curAnim["frames"])):
                return self.curAnim["frames"][math.floor(self.curFrame) - 1]
            else:
                return self.curAnim["frames"][0]
        elif self.__frames:
            return self.__frames["frames"][0]
        else:
            return None

    def getFrameWidth(self):
        frame = self.getCurrentFrame()
        if frame:
            return frame["quad"].width
        else:
            return self.width

    def getFrameHeight(self):
        frame = self.getCurrentFrame()
        if frame:
            return frame["quad"].height
        else:
            return self.height

    def getMidpoint(self):
        return (self.x + self.width * 0.5, self.y + self.height * 0.5)

    def play(self, anim, force = False, frame = None):
        if not force and self.curAnim and self.curAnim["name"] == anim and not self.animFinished:
            self.animPaused = False
            self.animPaused = False
            return
            
        self.curAnim = self.__animations[anim]
        self.curFrame = frame == None and 1 or frame
        self.animFinished = False
        self.animPaused = False

    def stop(self):
        if self.curAnim:
            self.animFinished = True
            self.animPaused = True

    def finish(self):
        if self.curAnim:
            self.stop()
            self.curFrame = len(self.curAnim["frames"])

    def unload(self):
        self.texture = None
        self.__frames = None
        self.__animations = None

    def update(self, deltaTime):
        if self.alive and self.exists and self.curAnim and not self.animFinished and not self.animPaused:
            self.curFrame += deltaTime * self.curAnim["framerate"]
            if self.curFrame >= len(self.curAnim["frames"]):
                if self.curAnim["looped"]: self.curFrame = 1
                else:
                    self.curFrame = len(self.curAnim["frames"]) - 1
                    self.animFinished = True

    def draw(self, screen, X= 0, Y = 0):
        if self.exists and self.alive and self.texture and (self.scale[0] > 0 and self.scale[1] > 0):
            if self.curAnim and self.curFrame and self.curFrame >= 0:
                frame = self.curAnim["frames"][math.floor(self.curFrame)-1]
            else:
                frame = None


            x, y, angle, sx, sy, ox, oy = self.x, self.y, self.angle, self.scale[0], self.scale[1], self.origin[0], self.origin[1]

            if frame:
                ox, oy = ox + frame["offset"][0], oy + frame["offset"][1]

            # apply the alpha
            self.texture.set_alpha(self.alpha * 255)

            # apply the scale
            #self.texture = pg.transform.scale(self.texture, (int(self.width * sx), int(self.height * sy))) # slow
            #self.texture = pg.transform.rotozoom(self.texture, 0, sx) # even slower
            #self.texture = pg.transform.scale2x(self.texture) # fastest, but blurry

            # apply the rotation
            #self.texture = pg.transform.rotate(self.texture, angle)

            if self.lastFlipX != self.flipX or self.lastFlipY != self.flipY:
                self.texture = pg.transform.flip(self.texture, self.flipX, self.flipY)
                self.lastFlipX = self.flipX
                self.lastFlipY = self.flipY

                # update the frames
                if self.__frames != None:
                    for f in self.__frames["frames"]:
                        f["quad"] = pg.Rect(
                            self.width - f["quad"].x - f["quad"].width,
                            f["quad"].y,
                            f["quad"].width,
                            f["quad"].height
                        )

            # since pygame sucks at transforming, only apply the scale and rotation if it changed
            if self.lastScale != self.scale:
                self.texture = pg.transform.scale(self.texture, (int(self.width * sx), int(self.height * sy)))
                self.lastScale = self.scale

                # resize all the frames
                if self.__frames != None:
                    for f in self.__frames["frames"]:
                        f["quad"] = pg.Rect(
                            f["quad"].x * sx,
                            f["quad"].y * sy,
                            f["quad"].width * sx,
                            f["quad"].height * sy
                        )

            if self.lastAngle != self.angle:
                self.texture = pg.transform.rotate(self.texture, angle)
                self.lastAngle = self.angle

            # apply the offset
            x, y = x - ox, y - oy
            x, y = x + int(self.offset[0]), y + int(self.offset[1])
            
            # apply the camera
            if self.camera != None:
                x, y = x - self.camera.x * self.scrollFactor[0], y - self.camera.y * self.scrollFactor[1]

            # apply cliprect to frame
            curQuad = frame != None and frame["quad"] or None

            if self.clipRect != None:
                if curQuad != None:
                    curQuad = curQuad.clip(self.clipRect)
                else:
                    curQuad = self.clipRect

            # draw the texture
            if frame != None:
                screen.blit(self.texture, (x+X, y+Y), curQuad)
            else:
                screen.blit(self.texture, (x+X, y+Y))
        

