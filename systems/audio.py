"""音频管理系统。"""
import pygame
from pathlib import Path
from typing import Optional


class AudioManager:
    def __init__(self, music_volume: float = 0.7, sfx_volume: float = 0.8):
        self._music_volume = music_volume
        self._sfx_volume = sfx_volume
        self._current_music: Optional[str] = None

    def play_music(self, path: str, loops: int = -1):
        if self._current_music == path:
            return
        p = Path(path)
        if p.exists():
            pygame.mixer.music.load(str(p))
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(loops)
            self._current_music = path

    def stop_music(self):
        pygame.mixer.music.stop()
        self._current_music = None

    def play_sfx(self, path: str) -> Optional[pygame.mixer.Sound]:
        p = Path(path)
        if p.exists():
            sound = pygame.mixer.Sound(str(p))
            sound.set_volume(self._sfx_volume)
            sound.play()
            return sound
        return None

    def set_music_volume(self, vol: float):
        self._music_volume = max(0, min(1, vol))
        pygame.mixer.music.set_volume(self._music_volume)

    def set_sfx_volume(self, vol: float):
        self._sfx_volume = max(0, min(1, vol))
