global waits
waits = []

def wait(duration, callback, args = []):
    waits.append([duration, callback, args])

def update(deltaTime):
    for w in waits:
        w[0] -= deltaTime
        if w[0] <= 0:
            # callback CAN be a lambda
            w[1](*w[2])
            waits.remove(w)