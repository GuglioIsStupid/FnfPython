import modules.Sprite as Sprite

class HealthIcon(Sprite.Sprite):
    frames = []
    def __init__(self, icon="face", flip=False):
        super().__init__(0, 0)
        self.icon = icon
        self._load("assets/images/icons/icon-" + self.icon + ".png")

        f0 = Sprite.Sprite._newFrame("i0", 0, 0, 150, self.height, (self.width == 300 and 300 or 150), self.height, 75, -75)
        f1 = Sprite.Sprite._newFrame("i1", 150, 0, 150, self.height, (self.width == 300 and 300 or 150), self.height, 75, -75)
        self.setFrames({
            "texture": Sprite.getImage("assets/images/icons/icon-" + self.icon + ".png"),
            "frames": [f0, f1]
        })
        self.addAnimByPrefix("icon", "i", 0, False)
        self.play("icon", True, 0)
        if self.width < 300: f1 = f0

        if flip: self.flipX = True

    def swap(self, frame):
        self.play("icon", True, frame)