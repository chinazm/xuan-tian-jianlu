"""音频管理系统。"""
import pygame
from pathlib import Path
from typing import Optional


class AudioManager:
    def __init__(self, music_volume: float = 0.7, sfx_volume: float = 0.8):
        self._music_volume = music_volume
        self._sfx_volume = sfx_volume
        self._current_music: Optional[str] = None
        self._music_available = True

    def play_music(self, path: str, loops: int = -1):
        if not self._music_available:
            return
        if self._current_music == path:
            return
        try:
            p = Path(path)
            if p.exists():
                pygame.mixer.music.load(str(p))
                pygame.mixer.music.set_volume(self._music_volume)
                pygame.mixer.music.play(loops)
                self._current_music = path
        except pygame.error as e:
            print(f"[AudioManager] play_music 失败 ({path}): {e}")
            self._music_available = False
        except Exception as e:
            print(f"[AudioManager] play_music 异常 ({path}): {e}")
            self._music_available = False

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._current_music = None

    def play_sfx(self, path: str) -> Optional[pygame.mixer.Sound]:
        if not self._music_available:
            return None
        try:
            p = Path(path)
            if p.exists():
                sound = pygame.mixer.Sound(str(p))
                sound.set_volume(self._sfx_volume)
                sound.play()
                return sound
        except pygame.error as e:
            print(f"[AudioManager] play_sfx 失败 ({path}): {e}")
            self._music_available = False
        except Exception as e:
            print(f"[AudioManager] play_sfx 异常 ({path}): {e}")
        return None

    def set_music_volume(self, vol: float):
        self._music_volume = max(0, min(1, vol))
        try:
            pygame.mixer.music.set_volume(self._music_volume)
        except Exception:
            pass

    def set_sfx_volume(self, vol: float):
        self._sfx_volume = max(0, min(1, vol))
