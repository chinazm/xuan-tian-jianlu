"""主菜单：开始游戏/继续/设置。"""
import pygame
from ui.base_ui import FontManager, TouchButton


class MainMenu:
    """主菜单界面。"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        self._selected_action: str = None
        self._active = True
        
        self._build_buttons()
    
    def _build_buttons(self):
        """构建主菜单按钮。"""
        s = self._scale
        btn_width = int(220 * s)
        btn_height = int(48 * s)
        spacing = int(16 * s)
        
        # 主菜单项
        items = [
            ("开始游戏", "start"),
            ("继续游戏", "continue"),
        ]
        
        # 居中排列
        total_h = len(items) * (btn_height + spacing)
        start_y = (self.height - total_h) // 2 + int(40 * s)
        center_x = (self.width - btn_width) // 2
        
        self._buttons: list[TouchButton] = []
        for i, (text, action) in enumerate(items):
            y = start_y + i * (btn_height + spacing)
            btn = TouchButton(center_x, y, btn_width, btn_height, text,
                            font_size=max(14, int(16 * s)),
                            bg_color=(30, 30, 50),
                            border_color=(80, 80, 120),
                            hover_color=(50, 50, 80),
                            pressed_color=(70, 70, 110),
                            action=action)
            
            def make_callback(act):
                def cb():
                    self._selected_action = act
                return cb
            
            btn.set_on_click(make_callback(action))
            self._buttons.append(btn)
        
        # 版本文字
        self._version_pos = (int(10 * s), self.height - int(20 * s))
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件。"""
        for btn in self._buttons:
            if btn.handle_touch(touch_pos, event_type):
                return True
        return False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染主菜单。"""
        if not self._active:
            return
        
        # 背景
        screen.fill((10, 10, 20))
        
        # 标题
        title = self.fm.render_text("玄天剑录", 32, (255, 215, 0), bold=True)
        screen.blit(title, (self.width // 2 - title.get_width() // 2, int(self.height * 0.2)))
        
        # 副标题
        subtitle = self.fm.render_text("像素仙侠 RPG", 16, (150, 150, 180))
        screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, int(self.height * 0.28)))
        
        # 按钮
        for btn in self._buttons:
            btn.render(screen)
        
        # 版本
        ver = self.fm.render_text("v0.1", 10, (80, 80, 80))
        screen.blit(ver, self._version_pos)
    
    @property
    def selected_action(self) -> str:
        action = self._selected_action
        self._selected_action = None
        return action
    
    @property
    def is_active(self) -> bool:
        return self._active
    
    def dismiss(self):
        """关闭主菜单。"""
        self._active = False
    
    def show(self):
        """显示主菜单。"""
        self._active = True
        self._selected_action = None
        for btn in self._buttons:
            btn.reset_state()
    
    def reset(self):
        """重置状态。"""
        self._selected_action = None
        for btn in self._buttons:
            btn.reset_state()
