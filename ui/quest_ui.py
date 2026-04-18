"""任务 UI：任务列表 + 进度显示。"""
import pygame
from ui.base_ui import FontManager, ProgressBar, TouchButton


class QuestUI:
    """任务界面。"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        # 面板
        self._panel_width = int(min(width * 0.8, 640 * self._scale))
        self._panel_height = int(min(height * 0.65, 400 * self._scale))
        self._panel_x = (width - self._panel_width) // 2
        self._panel_y = (height - self._panel_height) // 2
        
        # 滚动区域
        self._list_x = self._panel_x + int(16 * self._scale)
        self._list_y = self._panel_y + int(45 * self._scale)
        self._list_width = self._panel_width - int(32 * self._scale)
        self._item_height = int(70 * self._scale)
        
        # 关闭按钮
        self._close_btn = TouchButton(
            self._panel_x + self._panel_width - int(40 * self._scale),
            self._panel_y + int(8 * self._scale),
            int(32 * self._scale), int(32 * self._scale),
            "✕", font_size=max(12, int(14 * self._scale)),
            bg_color=(60, 30, 30),
            border_color=(120, 60, 60),
            action="close_quest"
        )
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件。"""
        return self._close_btn.handle_touch(touch_pos, event_type)
    
    def render(self, screen: pygame.Surface, quest_system) -> None:
        """渲染任务界面。"""
        # 半透明背景
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # 面板
        panel = pygame.Surface((self._panel_width, self._panel_height), pygame.SRCALPHA)
        panel.fill((20, 25, 35, 240))
        pygame.draw.rect(panel, (80, 80, 120), panel.get_rect(), 2)
        screen.blit(panel, (self._panel_x, self._panel_y))
        
        # 标题
        title = self.fm.render_text("任务", 18, (255, 215, 0), bold=True)
        screen.blit(title, (self._panel_x + int(16 * self._scale), self._panel_y + int(10 * self._scale)))
        
        # 活跃任务列表
        active_quests = getattr(quest_system, 'active_quests', [])
        completed_quests = getattr(quest_system, 'completed_quests', [])
        
        y = self._list_y
        for quest in active_quests:
            # 任务标题
            title_color = (100, 200, 100) if quest.completed else (220, 220, 220)
            title_surf = self.fm.render_text(
                f"{'✓ ' if quest.completed else ''}{quest.title}", 14, title_color, bold=True
            )
            screen.blit(title_surf, (self._list_x, y))
            y += int(22 * self._scale)
            
            # 任务描述
            desc_surf = self.fm.render_text(quest.description, 11, (160, 160, 160))
            screen.blit(desc_surf, (self._list_x + int(10 * self._scale), y))
            y += int(18 * self._scale)
            
            # 目标进度
            for obj in quest.objectives:
                progress = min(1.0, obj.current / obj.required) if obj.required > 0 else 0
                obj_text = f"{obj.target}: {obj.current}/{obj.required}"
                obj_surf = self.fm.render_text(obj_text, 11, (180, 180, 180))
                screen.blit(obj_surf, (self._list_x + int(16 * self._scale), y))
                y += int(14 * self._scale)
            
            y += int(6 * self._scale)
        
        # 无任务提示
        if not active_quests:
            none_surf = self.fm.render_text("暂无任务", 14, (120, 120, 120))
            screen.blit(none_surf, (self._list_x + int(20 * self._scale), self._list_y + int(30 * self._scale)))
        
        # 已完成任务
        if completed_quests:
            y += int(10 * self._scale)
            comp_title = self.fm.render_text("已完成", 12, (100, 100, 100))
            screen.blit(comp_title, (self._list_x, y))
            y += int(18 * self._scale)
            
            for q_id in completed_quests[-3:]:  # 最近 3 个
                comp_surf = self.fm.render_text(f"  ✓ {q_id}", 10, (100, 100, 100))
                screen.blit(comp_surf, (self._list_x, y))
                y += int(14 * self._scale)
        
        # 关闭按钮
        self._close_btn.render(screen)
    
    def reset(self):
        """重置状态。"""
        self._close_btn.reset_state()
