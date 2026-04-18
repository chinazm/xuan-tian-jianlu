"""背包 UI：网格显示 + 物品详情。"""
import pygame
from ui.base_ui import FontManager, TouchButton


class InventoryUI:
    """背包界面。"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        # 面板
        self._panel_width = int(min(width * 0.85, 680 * self._scale))
        self._panel_height = int(min(height * 0.7, 420 * self._scale))
        self._panel_x = (width - self._panel_width) // 2
        self._panel_y = (height - self._panel_height) // 2
        
        # 物品网格 (5x4)
        self._cols = 5
        self._rows = 4
        self._slot_size = int(60 * self._scale)
        self._slot_spacing = int(6 * self._scale)
        self._grid_x = self._panel_x + int(16 * self._scale)
        self._grid_y = self._panel_y + int(50 * self._scale)
        
        # 物品详情区域
        self._detail_y = self._grid_y + self._rows * (self._slot_size + self._slot_spacing) + int(12 * self._scale)
        self._detail_x = self._panel_x + int(16 * self._scale)
        self._detail_width = self._panel_width - int(32 * self._scale)
        
        # 关闭按钮
        self._close_btn = TouchButton(
            self._panel_x + self._panel_width - int(40 * self._scale),
            self._panel_y + int(8 * self._scale),
            int(32 * self._scale), int(32 * self._scale),
            "✕", font_size=max(12, int(14 * self._scale)),
            bg_color=(60, 30, 30),
            border_color=(120, 60, 60),
            action="close_inventory"
        )
        
        self._selected_slot: int = None
        self._slots: list[pygame.Rect] = []
        self._build_slots()
    
    def _build_slots(self):
        """构建物品槽位。"""
        self._slots.clear()
        for row in range(self._rows):
            for col in range(self._cols):
                x = self._grid_x + col * (self._slot_size + self._slot_spacing)
                y = self._grid_y + row * (self._slot_size + self._slot_spacing)
                self._slots.append(pygame.Rect(x, y, self._slot_size, self._slot_size))
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件。"""
        if self._close_btn.handle_touch(touch_pos, event_type):
            return True
        
        x, y = touch_pos
        if event_type == pygame.FINGERDOWN:
            for i, slot in enumerate(self._slots):
                if slot.collidepoint(x, y):
                    self._selected_slot = i
                    return True
        
        return False
    
    def render(self, screen: pygame.Surface, inventory) -> None:
        """渲染背包界面。"""
        # 全屏半透明
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # 面板背景
        panel = pygame.Surface((self._panel_width, self._panel_height), pygame.SRCALPHA)
        panel.fill((25, 25, 40, 240))
        pygame.draw.rect(panel, (80, 80, 120), panel.get_rect(), 2)
        screen.blit(panel, (self._panel_x, self._panel_y))
        
        # 标题
        title = self.fm.render_text("背包", 18, (255, 215, 0), bold=True)
        screen.blit(title, (self._panel_x + int(16 * self._scale), self._panel_y + int(10 * self._scale)))
        
        # 灵石数
        lingshi = self.fm.render_text(f"灵石: {getattr(inventory, 'lingshi', 0)}", 13, (200, 200, 200))
        screen.blit(lingshi, (self._panel_x + int(80 * self._scale), self._panel_y + int(12 * self._scale)))
        
        # 物品槽位
        items = getattr(inventory, '_items', [])
        for i, slot in enumerate(self._slots):
            # 槽位背景
            bg_color = (40, 40, 60) if i != self._selected_slot else (60, 60, 100)
            pygame.draw.rect(screen, bg_color, slot)
            pygame.draw.rect(screen, (80, 80, 120), slot, 1)
            
            # 物品信息
            if i < len(items):
                item = items[i]
                name = self.fm.render_text(item.name, 11, (200, 200, 220))
                screen.blit(name, (slot.x + int(4 * self._scale), slot.y + int(4 * self._scale)))
                
                if item.quantity > 1:
                    qty = self.fm.render_text(f"x{item.quantity}", 10, (180, 180, 180))
                    screen.blit(qty, (slot.right - qty.get_width() - int(4 * self._scale),
                                     slot.bottom - qty.get_height() - int(2 * self._scale)))
        
        # 选中物品详情
        if self._selected_slot is not None and self._selected_slot < len(items):
            item = items[self._selected_slot]
            detail_lines = [
                self.fm.render_text(item.name, 15, (255, 215, 0), bold=True),
                self.fm.render_text(f"类型: {item.type}", 12, (180, 180, 180)),
                self.fm.render_text(f"数量: {item.quantity}/{item.max_stack}", 12, (180, 180, 180)),
            ]
            if item.description:
                detail_lines.append(self.fm.render_text(item.description, 11, (150, 150, 150)))
            
            y = self._detail_y
            for surf in detail_lines:
                screen.blit(surf, (self._detail_x, y))
                y += surf.get_height() + int(4 * self._scale)
        
        # 关闭按钮
        self._close_btn.render(screen)
    
    @property
    def selected_item_index(self) -> int:
        idx = self._selected_slot
        self._selected_slot = None
        return idx
    
    def reset(self):
        """重置状态。"""
        self._selected_slot = None
        self._close_btn.reset_state()
