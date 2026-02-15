from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

class MusicManager:
    def __init__(self):
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.tracks = {}
        self.current_track = None

        self.audio_output.setVolume(0.4)

    def load(self, name: str, path: str):
        self.tracks[name] = path

    def play(self, name: str):
        if name not in self.tracks:
            return

        if self.current_track == name:
            return  # already playing

        self.player.stop()

        self.player.setSource(QUrl.fromLocalFile(self.tracks[name]))
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.play()

        self.current_track = name

    def stop(self):
        self.player.stop()
        self.current_track = None

    # ---- Volume Control ----

    def set_volume(self, value: float):
        """Set volume between 0.0 and 1.0"""
        value = max(0.0, min(1.0, value))
        self.audio_output.setVolume(value)

    def set_volume_percent(self, percent: int):
        """Set volume between 0 and 100 (UI slider friendly)"""
        percent = max(0, min(100, percent))
        self.audio_output.setVolume(percent / 100.0)

    def get_volume(self) -> float:
        return self.audio_output.volume()

    def get_volume_percent(self) -> int:
        return int(self.audio_output.volume() * 100)


class SoundManager:
    def __init__(self):
        self.sounds = {}

    def load(self, name: str, path: str, volume: float = 0.5, loop=False):
        sound = QSoundEffect()
        sound.setSource(QUrl.fromLocalFile(path))
        sound.setVolume(volume)
        self.sounds[name] = sound
        if loop:
            sound.setLoopCount(QSoundEffect.Infinite)

    def play(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()