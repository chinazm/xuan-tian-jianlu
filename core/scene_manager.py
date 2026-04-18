"""场景管理器：场景切换 + 淡入淡出过渡。"""
import pygame
from typing import Optional
from core.logger import GameLogger

logger = GameLogger.get("scene")


class Scene:
    """场景基类。每个场景实现自己的 update 和 render。"""

    def __init__(self, name: str):
        self.name = name

    def on_enter(self) -> None:
        logger.info(f"Entering scene: {self.name}")

    def on_exit(self) -> None:
        logger.info(f"Exiting scene: {self.name}")

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass


class SceneManager:
    def __init__(self):
        self._scenes: dict[str, Scene] = {}
        self._current: Optional[Scene] = None
        self._transition = None

    def register(self, scene: Scene) -> None:
        self._scenes[scene.name] = scene

    def switch_to(self, scene_name: str, fade_duration: float = 0.5) -> None:
        if scene_name not in self._scenes:
            logger.error(f"Scene not found: {scene_name}")
            return

        self._transition = {
            "phase": "fade_out",
            "alpha": 0.0,
            "duration": fade_duration,
            "elapsed": 0.0,
            "next_scene": scene_name,
        }

    def set_immediate(self, scene_name: str) -> None:
        if self._current:
            self._current.on_exit()
        self._current = self._scenes[scene_name]
        self._current.on_enter()

    def update(self, dt: float) -> None:
        if self._transition:
            self._transition["elapsed"] += dt
            progress = self._transition["elapsed"] / self._transition["duration"]

            if self._transition["phase"] == "fade_out":
                self._transition["alpha"] = min(1.0, progress)
                if progress >= 1.0:
                    next_name = self._transition["next_scene"]
                    if self._current:
                        self._current.on_exit()
                    self._current = self._scenes[next_name]
                    self._current.on_enter()
                    self._transition["phase"] = "fade_in"
                    self._transition["elapsed"] = 0.0

            elif self._transition["phase"] == "fade_in":
                self._transition["alpha"] = max(0.0, 1.0 - progress)
                if progress >= 1.0:
                    self._transition = None

            if self._current:
                self._current.update(dt)
        else:
            if self._current:
                self._current.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        if self._current:
            self._current.render(screen)

        if self._transition:
            alpha = int(self._transition["alpha"] * 255)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._current:
            self._current.handle_event(event)

    @property
    def current_scene_name(self) -> Optional[str]:
        return self._current.name if self._current else None
