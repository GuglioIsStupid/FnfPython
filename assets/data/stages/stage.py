import modules.Stage as Stage
import modules.Sprite as Sprite
import modules.Camera as Camera

class Stage(Stage.BaseStage):
    camera = None
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

        self.back = Sprite.Sprite(-600, -200)
        self.back._load("assets/images/stages/stage/stageback.png")
        self.back.scrollFactor = (0.9, 0.9)
        self.back.camera = self.camera

        self.front = Sprite.Sprite(-650, 600)
        self.front._load("assets/images/stages/stage/stagefront.png")
        self.front.scale = (1.1, 1.1)
        self.front.scrollFactor = (0.9, 0.9)
        self.front.camera = self.camera

        self.curtains = Sprite.Sprite(-500, -300)
        self.curtains._load("assets/images/stages/stage/stagecurtains.png")
        self.curtains.scale = (0.9, 0.9)
        self.curtains.scrollFactor = (1.3, 1.3)
        

    def update(self, deltaTime):
        super().update(deltaTime)

    def draw(self, screen):
        super().draw(screen)
        self.back.draw(screen)
        self.front.draw(screen)
        self.curtains.draw(screen)