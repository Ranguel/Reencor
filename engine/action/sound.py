from engine.math.probability import weighted_choice


def play_voice_sound_effect(self: object, value="reencor/nota", **kwargs):
    """Plays sound from the object. This sound can be interrupted. 'folder/file name'. 'Voice': 'Name'"""
    value = weighted_choice(value)
    if value == "none":
        return


def play_sound_effect(self: object, value="reencor/nota", **kwargs):
    """Plays sound from the object. This sound can not be interrupted. 'folder/file name'. 'Sound': 'Name'"""
    self.sound.append(value)


SOUND_ACT = {
    "voice": play_voice_sound_effect,
    "sound": play_sound_effect,
}
