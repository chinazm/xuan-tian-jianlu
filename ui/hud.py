"""游戏内 HUD：气血条、灵力条、境界、灵石、快捷栏。支持动态缩放。"""
import pygame
from ui.base_ui import FontManager, ProgressBar, TouchButton


class HUD:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        self._init_layout()
    
    def _init_layout(self):
        """根据屏幕尺寸计算布局。"""
        s = self._scale
        bar_width = int(160 * s)
        bar_height = int(14 * s)
        
        # 顶部状态条背景高度
        self._bg_height = int(44 * s)
        
        # 气血条
        self._hp_bar = ProgressBar(
            int(10 * s), int(8 * s), bar_width, bar_height,
            fill_color=(200, 50, 50)
        )
        # 灵力条
        self._mp_bar = ProgressBar(
            int(10 * s), int(26 * s), bar_width, bar_height,
            fill_color=(50, 100, 200)
        )
        
        # 境界文字位置
        self._realm_pos = (self.width // 2, int(10 * s))
        
        # 灵石文字位置
        self._lingshi_pos = (self.width - int(10 * s), int(10 * s))
        
        # 快捷技能栏按钮（右下角）
        btn_size = int(40 * s)
        spacing = int(6 * s)
        skill_keys = ["J 攻", "K 技", "L 闪", "E 交"]
        self._skill_buttons: list[TouchButton] = []
        
        for i, label in enumerate(skill_keys):
            x = self.width - (4 * (btn_size + spacing)) + i * (btn_size + spacing)
            y = self.height - btn_size - int(8 * s)
            btn = TouchButton(x, y, btn_size, btn_size, label,
                            font_size=max(10, int(11 * s)),
                            bg_color=(30, 30, 50),
                            border_color=(80, 80, 120),
                            action=f"skill_{i}")
            self._skill_buttons.append(btn)
        
        # 菜单按钮（右上角）
        menu_btn_size = int(32 * s)
        self._menu_button = TouchButton(
            self.width - menu_btn_size - int(10 * s),
            int(6 * s),
            menu_btn_size, menu_btn_size,
            "☰", font_size=max(12, int(16 * s)),
            bg_color=(40, 40, 60),
            border_color=(80, 80, 120),
            action="menu"
        )
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理 HUD 区域的触摸事件。"""
        consumed = False
        
        # 菜单按钮
        if self._menu_button.handle_touch(touch_pos, event_type):
            consumed = True
        
        # 技能按钮
        for btn in self._skill_buttons:
            if btn.handle_touch(touch_pos, event_type):
                consumed = True
        
        return consumed
    
    def render(self, screen: pygame.Surface, player_state: dict) -> None:
        # 背景半透明条
        bg = pygame.Surface((self.width, self._bg_height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        screen.blit(bg, (0, 0))
        
        # 气血条
        self._hp_bar.set_value(player_state.get("current_hp", 100),
                               player_state.get("max_hp", 100))
        self._hp_bar.render(screen)
        
        # 灵力条
        self._mp_bar.set_value(player_state.get("current_mp", 0),
                               player_state.get("max_mp", 100))
        self._mp_bar.render(screen)
        
        # 境界
        realm_text = f"{player_state.get('realm', '炼气期')} 第{player_state.get('realm_level', 1)}层"
        realm_surf = self.fm.render_text(realm_text, 16, (255, 215, 0), bold=True)
        screen.blit(realm_surf, (self._realm_pos[0] - realm_surf.get_width() // 2, self._realm_pos[1]))
        
        # 灵石
        lingshi_text = f"灵石: {player_state.get('lingshi', 0)}"
        ls_surf = self.fm.render_text(lingshi_text, 12, (200, 200, 200))
        screen.blit(ls_surf, (self._lingshi_pos[0] - ls_surf.get_width(), self._lingshi_pos[1]))
        
        # 快捷技能栏
        for btn in self._skill_buttons:
            btn.render(screen)
        
        # 菜单按钮
        self._menu_button.render(screen)
    
    def reset(self):
        """重置按钮状态。"""
        self._menu_button.reset_state()
        for btn in self._skill_buttons:
            btn.reset_state()
