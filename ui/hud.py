"""游戏内 HUD：气血条、灵力条、境界、灵石、快捷栏。"""
import pygame
from core.config import WindowConfig


class HUD:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("sans-serif", 16)
        self.font_bold = pygame.font.SysFont("sans-serif", 18, bold=True)
        self.font_small = pygame.font.SysFont("sans-serif", 12)
        self.bar_height = 12
        self.bar_width = 160

    def render(self, screen: pygame.Surface, player_state: dict) -> None:
        # 背景半透明条
        bg = pygame.Surface((self.width, 40), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        screen.blit(bg, (0, 0))

        x, y = 10, 8
        # 气血条
        self._draw_bar(screen, x, y, player_state.get("current_hp", 100),
                       player_state.get("max_hp", 100), (200, 50, 50), "气血")
        # 灵力条
        self._draw_bar(screen, x, y + 20, player_state.get("current_mp", 0),
                       player_state.get("max_mp", 100), (50, 50, 200), "灵力")

        # 境界
        realm_text = f"{player_state.get('realm', '炼气期')} 第{player_state.get('realm_level', 1)}层"
        realm_surf = self.font_bold.render(realm_text, True, (255, 215, 0))
        screen.blit(realm_surf, (self.width // 2 - realm_surf.get_width() // 2, 8))

        # 灵石
        lingshi_text = f"灵石: {player_state.get('lingshi', 0)}"
        ls_surf = self.font.render(lingshi_text, True, (200, 200, 200))
        screen.blit(ls_surf, (self.width - ls_surf.get_width() - 10, 8))

        # 快捷技能栏
        skills = player_state.get("skills", ["普通攻击", "御剑术"])
        for i, skill in enumerate(skills[:4]):
            key = ["J", "K", "L", "U"][i]
            box = pygame.Rect(self.width - 200 + i * 48, self.height - 40, 44, 36)
            pygame.draw.rect(screen, (40, 40, 60), box)
            pygame.draw.rect(screen, (100, 100, 140), box, 1)
            txt = self.font_small.render(key, True, (180, 180, 200))
            screen.blit(txt, (box.x + 2, box.y + 2))
            name = self.font_small.render(skill[:3], True, (200, 200, 200))
            screen.blit(name, (box.x + 2, box.y + 18))

    def _draw_bar(self, screen: pygame.Surface, x: int, y: int, current: float, maximum: float, color: tuple, label: str) -> None:
        ratio = max(0, min(1, current / maximum if maximum > 0 else 0))
        pygame.draw.rect(screen, (40, 40, 40), (x, y, self.bar_width, self.bar_height))
        pygame.draw.rect(screen, color, (x, y, int(self.bar_width * ratio), self.bar_height))
        text = self.font_small.render(f"{label}: {int(current)}/{int(maximum)}", True, (255, 255, 255))
        screen.blit(text, (x + 4, y - 1))
