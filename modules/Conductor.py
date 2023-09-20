global time, beat, lastBeat, bpm, beatHit
time = 0
beat = 0
lastBeat = 0
bpm = 120
beatHit = False

crochet = (60 / bpm) * 1000
stepCrochet = crochet / 4

def update(deltaTime):
    global time, beat, lastBeat, beatHit
    time += deltaTime
    beat = time * bpm / 60
    beatHit = False

    if int(beat) > int(lastBeat):
        lastBeat = beat
        beatHit = True

        
def getBeat():
    return beat

def getBeatHit():
    return beatHit
