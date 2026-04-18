"""对话 UI：气泡渲染 + 选项按钮。"""
import pygame
from ui.base_ui import FontManager, TouchButton


class DialogueUI:
    """对话界面渲染器。"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        # 对话面板尺寸
        self._panel_padding = int(20 * self._scale)
        self._panel_width = int(min(width * 0.85, 700 * self._scale))
        self._panel_height = int(200 * self._scale)
        self._panel_x = (width - self._panel_width) // 2
        self._panel_y = height - self._panel_height - int(80 * self._scale)
        
        # 说话者标签
        self._speaker_pos = (self._panel_x + self._panel_padding,
                            self._panel_y - int(28 * self._scale))
        
        # 文字区域
        self._text_x = self._panel_x + self._panel_padding + int(10 * self._scale)
        self._text_y = self._panel_y + int(40 * self._scale)
        self._text_width = self._panel_width - self._panel_padding * 2 - int(20 * self._scale)
        self._text_height = self._panel_height - int(100 * self._scale)
        
        # 选项按钮
        self._choice_buttons: list[TouchButton] = []
        
        # 提示文字
        self._hint_pos = (self._panel_x + self._panel_width - int(80 * self._scale),
                         self._panel_y + self._panel_height - int(25 * self._scale))
    
    def _wrap_text(self, text: str, max_width: int, font_size: int) -> list[pygame.Surface]:
        """文字自动换行。"""
        font = self.fm.get_font(font_size)
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            if font.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        return [font.render(line, True, (220, 220, 220)) for line in lines]
    
    def _build_choice_buttons(self, choices: list[dict]):
        """根据选项创建按钮。"""
        self._choice_buttons.clear()
        
        if not choices:
            return
        
        btn_width = int(min(200 * self._scale, (self._panel_width - self._panel_padding * 3) / len(choices)))
        btn_height = int(36 * self._scale)
        total_width = len(choices) * btn_width + (len(choices) - 1) * int(10 * self._scale)
        start_x = (self._panel_width - total_width) // 2 + self._panel_x
        
        for i, choice in enumerate(choices):
            x = start_x + i * (btn_width + int(10 * self._scale))
            y = self._panel_y + self._panel_height - btn_height - int(8 * self._scale)
            
            def make_callback(idx):
                def callback():
                    self._selected_choice = idx
                return callback
            
            btn = TouchButton(x, y, btn_width, btn_height,
                            choice.get("text", f"选项{i+1}"),
                            font_size=max(11, int(13 * self._scale)),
                            bg_color=(40, 50, 70),
                            border_color=(100, 120, 160),
                            action=f"choice_{i}")
            btn.set_on_click(make_callback(i))
            self._choice_buttons.append(btn)
        
        self._selected_choice = None
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件。"""
        for btn in self._choice_buttons:
            if btn.handle_touch(touch_pos, event_type):
                return True
        return False
    
    def render(self, screen: pygame.Surface, dialogue_system) -> None:
        """渲染对话界面。"""
        if not dialogue_system.is_active():
            return
        
        line = dialogue_system.current_line()
        if not line:
            return
        
        # 半透明背景覆盖
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        # 对话面板
        panel_surf = pygame.Surface((self._panel_width, self._panel_height), pygame.SRCALPHA)
        panel_surf.fill((20, 25, 40, 230))
        pygame.draw.rect(panel_surf, (100, 120, 160), panel_surf.get_rect(), 2)
        screen.blit(panel_surf, (self._panel_x, self._panel_y))
        
        # 说话者
        speaker = line.get("speaker", "???")
        speaker_surf = self.fm.render_text(speaker, 14, (255, 215, 0), bold=True)
        screen.blit(speaker_surf, self._speaker_pos)
        
        # 对话文字
        text = line.get("text", "")
        text_surfaces = self._wrap_text(text, self._text_width, 13)
        y_pos = self._text_y
        for surf in text_surfaces:
            screen.blit(surf, (self._text_x, y_pos))
            y_pos += surf.get_height() + int(4 * self._scale)
        
        # 如果有选项，渲染选项按钮
        choices = dialogue_system.get_choices()
        if choices:
            self._build_choice_buttons(choices)
            for btn in self._choice_buttons:
                btn.render(screen)
        else:
            # 无选项时显示"点击继续"提示
            hint_surf = self.fm.render_text("▼ 点击继续", 11, (150, 150, 150))
            screen.blit(hint_surf, self._hint_pos)
    
    def get_selected_choice(self) -> int:
        """获取已选择的选项索引。"""
        idx = self._selected_choice
        self._selected_choice = None
        return idx
    
    def reset(self):
        """重置状态。"""
        self._choice_buttons.clear()
        self._selected_choice = None
