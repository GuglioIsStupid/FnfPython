curScene = None

class Base(object):
    def __init__(self):
        pass

    def update(self):
        raise NotImplementedError
    
    def render(self, screen):
        raise NotImplementedError

    def handle_events(self, events = None):
        raise NotImplementedError