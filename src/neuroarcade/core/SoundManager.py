from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

class MusicManager:
    """
    Music manager class for background music for the Arcade.
    Pre-loads the  available songs, reproduce those stop them and change volume.
    """
    def __init__(self, initial_volume=0.4):
        """Initializes the MusicManager instance using `QMediaPlayer` and `QAudioOutput`
        
        Args:
            initial_volume (float, optional): Initial volume for the music. Defaults to 0.4.
        """
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.tracks = {}
        self.current_track = None

        self.audio_output.setVolume(initial_volume)

    def load(self, name: str, path: str):
        """Stores the name of a song and it's location for easy playing.

        Args:
            name (str): Name of the song to store. Will be played using that name.
            path (str): Path to the location of the audio file.
        """
        self.tracks[name] = path

    def play(self, name: str):
        """Play the specified song. If one is playing then that is stopped and the
        new one played.

        Args:
            name (str): Name of the stored song.

        Returns:
            None: Just plays the new sound.
        """
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
        """Stop the current music.
        """
        self.player.stop()
        self.current_track = None

    # ---- Volume Control ----

    def set_volume(self, value: float):
        """Set volume between 0.0 and 1.0

        Args:
            value (float): New volume
        """
        value = max(0.0, min(1.0, value))
        self.audio_output.setVolume(value)

    def set_volume_percent(self, percent: int):
        """Set volume between 0 and 100 (UI slider friendly)

        Args:
            percent (int): Volume level in percentage
        """
        percent = max(0, min(100, percent))
        self.audio_output.setVolume(percent / 100.0)

    def get_volume(self) -> float:
        """Returns the current volume.

        Returns:
            float: Volume of the current playback from 0 to 1.
        """
        return self.audio_output.volume()

    def get_volume_percent(self) -> int:
        """Returns the current volume.

        Returns:
            int: Volume of the current playback from 0 to 100.
        """
        return int(self.audio_output.volume() * 100)


class SoundManager:
    """
    Class used by the games to play sound effects. This class loads all the effects
    and are available by their name to the games. Plays one at the time, no loop.
    """
    def __init__(self):
        """Initializes the available effects dictionary.
        """
        self.sounds = {}

    def load(self, name: str, path: str, volume: float = 0.5, loop=False):
        """Stores an effect under a specific name, in a specific path and will be played
        at specific volume. This allows the definition of each effect and a custom volume
        for each one.

        Args:
            name (str): Name of the effect.
            path (str): Path of the sound file.
            volume (float, optional): Volume of the effect. Defaults to 0.5.
            loop (bool, optional): Whether or not to loop the sound. Defaults to False.
        """
        sound = QSoundEffect()
        sound.setSource(QUrl.fromLocalFile(path))
        sound.setVolume(volume)
        self.sounds[name] = sound
        if loop:
            sound.setLoopCount(QSoundEffect.Infinite)

    def play(self, name: str):
        """Plays the effect with the specified name.

        Args:
            name (str): Name of the sound effect.
        """
        if name in self.sounds:
            self.sounds[name].play()