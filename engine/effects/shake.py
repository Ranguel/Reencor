import math

class ShakeComponent:
    def __init__(self):
        self.time = 0.0
        self.amplitude = 0.0
        self.frequency = 40.0
        self.damping = 6.0
        self.active = False
        self.offset = (0.0, 0.0)
        self.duration = None

    def trigger(self, strength, direction=(1, 0), duration=None, damping=6.0):
        self.active = True
        self.amplitude = strength
        self.time = 0.0
        self.direction = direction

        if duration is not None:
            self.duration = duration
        else:
            self.duration = None

        if damping is not None:
            self.damping = damping

    def update(self, dt):
        if not self.active:
            self.offset = (0.0, 0.0)
            return (0,0,0)

        self.time += dt

        if self.duration is not None and self.time >= self.duration:
            self.active = False
            self.amplitude = 0.0
            self.offset = (0.0, 0.0)
            return (0,0,0)

        decay = math.exp(-self.damping * self.time)
        amp = self.amplitude * decay

        if amp < 0.001:
            self.active = False
            self.amplitude = 0.0
            self.offset = (0.0, 0.0)
            return (0,0,0)

        magnitude = amp * math.sin(self.frequency * self.time)

        ox = magnitude * self.direction[0]
        oy = magnitude * self.direction[1]

        self.offset = (ox, oy)
        return (ox, oy, 0)