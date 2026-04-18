"""修炼 UI：境界信息 + 灵力进度 + 突破按钮。"""
import pygame
from ui.base_ui import FontManager, ProgressBar, TouchButton


class CultivationUI:
    """修炼界面。"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        # 面板
        self._panel_width = int(min(width * 0.8, 640 * self._scale))
        self._panel_height = int(300 * self._scale)
        self._panel_x = (width - self._panel_width) // 2
        self._panel_y = (height - self._panel_height) // 2
        
        # 灵力进度条
        bar_width = int(self._panel_width - int(60 * self._scale))
        bar_height = int(20 * self._scale)
        self._lingli_bar = ProgressBar(
            int(30 * self._scale),
            self._panel_y + int(100 * self._scale),
            bar_width, bar_height,
            fill_color=(100, 50, 200)
        )
        
        # 突破按钮
        btn_w = int(160 * self._scale)
        btn_h = int(44 * self._scale)
        self._breakthrough_btn = TouchButton(
            (width - btn_w) // 2,
            self._panel_y + int(160 * self._scale),
            btn_w, btn_h,
            "突破", font_size=max(13, int(16 * self._scale)),
            bg_color=(50, 30, 80),
            border_color=(120, 80, 200),
            hover_color=(70, 40, 110),
            pressed_color=(90, 50, 140),
            action="breakthrough"
        )
        
        # 关闭按钮
        self._close_btn = TouchButton(
            self._panel_x + self._panel_width - int(40 * self._scale),
            self._panel_y + int(8 * self._scale),
            int(32 * self._scale), int(32 * self._scale),
            "✕", font_size=max(12, int(14 * self._scale)),
            bg_color=(60, 30, 30),
            border_color=(120, 60, 60),
            action="close_cultivation"
        )
        
        self._breakthrough_requested = False
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件。"""
        if self._close_btn.handle_touch(touch_pos, event_type):
            return True
        if self._breakthrough_btn.handle_touch(touch_pos, event_type):
            self._breakthrough_requested = True
            return True
        return False
    
    def render(self, screen: pygame.Surface, cultivation) -> None:
        """渲染修炼界面。"""
        # 半透明背景
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # 面板
        panel = pygame.Surface((self._panel_width, self._panel_height), pygame.SRCALPHA)
        panel.fill((20, 15, 35, 240))
        pygame.draw.rect(panel, (100, 80, 160), panel.get_rect(), 2)
        screen.blit(panel, (self._panel_x, self._panel_y))
        
        # 标题
        title = self.fm.render_text("修炼", 20, (255, 215, 0), bold=True)
        screen.blit(title, (self._panel_x + int(16 * self._scale), self._panel_y + int(10 * self._scale)))
        
        # 境界
        realm = getattr(cultivation, 'current_realm_name', '未知')
        level = getattr(cultivation, 'realm_level', 1)
        realm_text = f"{realm} 第{level}层"
        realm_surf = self.fm.render_text(realm_text, 18, (220, 220, 220), bold=True)
        screen.blit(realm_surf, (self._panel_x + (self._panel_width - realm_surf.get_width()) // 2,
                                self._panel_y + int(50 * self._scale)))
        
        # 灵力
        lingli = getattr(cultivation, 'lingli', 0)
        progress = cultivation.get_progress() if hasattr(cultivation, 'get_progress') else 0
        max_lingli = 100  # fallback
        
        # 尝试从 realm data 获取最大值
        try:
            exp_list = cultivation.current_realm_data.get("exp_to_next", [])
            if exp_list and level <= len(exp_list):
                max_lingli = exp_list[level - 1]
        except Exception:
            pass
        
        self._lingli_bar.set_value(lingli, max_lingli)
        self._lingli_bar.render(screen)
        
        # 灵力文字
        lingli_text = f"灵力: {int(lingli)} / {int(max_lingli)} ({int(progress * 100)}%)"
        lingli_surf = self.fm.render_text(lingli_text, 12, (180, 180, 180))
        screen.blit(lingli_surf, (self._panel_x + int(30 * self._scale),
                                 self._panel_y + int(125 * self._scale)))
        
        # 突破按钮
        self._breakthrough_btn.render(screen)
        
        # 关闭按钮
        self._close_btn.render(screen)
    
    @property
    def breakthrough_requested(self) -> bool:
        requested = self._breakthrough_requested
        self._breakthrough_requested = False
        return requested
    
    def reset(self):
        """重置状态。"""
        self._breakthrough_requested = False
        self._close_btn.reset_state()
        self._breakthrough_btn.reset_state()
