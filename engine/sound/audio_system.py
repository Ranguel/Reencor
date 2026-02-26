class AudioSystem:
    def __init__(self):
        self.audio_queue = []

    def play(self, audio_event):
        pass

    def update(self):
        for event in self.audio_queue:
            self.play(event)
        self.audio_queue.clear()
