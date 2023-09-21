import modules.Wait as Wait
curScene = None
lastScene = None

class Base(object):
    def __init__(self):
        pass

    def update(self, deltaTime = 0):
        raise NotImplementedError
    
    def render(self, screen):
        raise NotImplementedError

    def handle_events(self, events = None):
        raise NotImplementedError

def setScene(scene):
    global curScene, lastScene
    lastScene = curScene
    if lastScene != None:
        lastScene.__unload__()
    curScene = scene
