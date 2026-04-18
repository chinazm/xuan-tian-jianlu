"""暂停菜单：存档/读档/设置/退出。"""
import pygame
from ui.base_ui import FontManager, TouchButton


class PauseMenu:
    """暂停菜单界面。"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        self._selected_action: str = None
        self._selected_slot: int = None
        
        self._build_buttons()
    
    def _build_buttons(self):
        """构建菜单按钮。"""
        s = self._scale
        btn_width = int(200 * s)
        btn_height = int(44 * s)
        spacing = int(12 * s)
        
        menu_items = [
            ("继续游戏", "resume"),
            ("存档", "save"),
            ("读档", "load"),
            ("修炼", "cultivate"),
            ("背包", "inventory"),
            ("任务", "quest"),
            ("退出游戏", "quit"),
        ]
        
        total_h = len(menu_items) * (btn_height + spacing)
        start_y = (self.height - total_h) // 2
        center_x = (self.width - btn_width) // 2
        
        self._buttons: list[TouchButton] = []
        for i, (text, action) in enumerate(menu_items):
            y = start_y + i * (btn_height + spacing)
            btn = TouchButton(center_x, y, btn_width, btn_height, text,
                            font_size=max(13, int(15 * s)),
                            bg_color=(35, 35, 55),
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
        
        # 存档槽位按钮（仅在选择存档/读档时显示）
        self._slot_buttons: list[TouchButton] = []
        slot_y = start_y + 3 * (btn_height + spacing)
        for i in range(3):
            x = (self.width - 3 * (btn_width + spacing)) // 2 + i * (btn_width + spacing)
            slot_btn = TouchButton(x, slot_y, btn_width, btn_height, f"存档 {i+1}",
                                 font_size=max(12, int(14 * s)),
                                 bg_color=(30, 40, 50),
                                 border_color=(70, 90, 120),
                                 action=f"slot_{i+1}")
            
            def make_slot_callback(slot):
                def cb():
                    self._selected_slot = slot
                return cb
            
            slot_btn.set_on_click(make_slot_callback(i + 1))
            self._slot_buttons.append(slot_btn)
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件。"""
        for btn in self._buttons:
            if btn.handle_touch(touch_pos, event_type):
                return True
        
        if self._show_slots:
            for btn in self._slot_buttons:
                if btn.handle_touch(touch_pos, event_type):
                    return True
        
        return False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染暂停菜单。"""
        # 全屏半透明遮罩
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 标题
        title = self.fm.render_text("玄天剑录", 24, (255, 215, 0), bold=True)
        screen.blit(title, (self.width // 2 - title.get_width() // 2, int(40 * self._scale)))
        
        # 菜单按钮
        for btn in self._buttons:
            btn.render(screen)
        
        # 存档槽位
        if self._show_slots:
            for btn in self._slot_buttons:
                btn.render(screen)
    
    @property
    def selected_action(self) -> str:
        action = self._selected_action
        self._selected_action = None
        return action
    
    @property
    def selected_slot(self) -> int:
        slot = self._selected_slot
        self._selected_slot = None
        return slot
    
    @property
    def _show_slots(self) -> bool:
        return self._selected_action in ("save", "load")
    
    def reset(self):
        """重置状态。"""
        self._selected_action = None
        self._selected_slot = None
        for btn in self._buttons:
            btn.reset_state()
        for btn in self._slot_buttons:
            btn.reset_state()
