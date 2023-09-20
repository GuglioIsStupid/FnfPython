def lerp(a, b, t):
    return a + (b - a) * t

def coolLerp(a, b, t, deltaTime):
    return a + (b - a) * (t * deltaTime)

def clamp(val, minVal, maxVal):
    return min(max(val, minVal), maxVal)