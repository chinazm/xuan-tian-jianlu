"""UI 基类：中文字体加载 + 动态缩放 + 通用 UI 组件。"""
import pygame
from pathlib import Path
from typing import Optional


# --- 字体管理器 ---
class FontManager:
    """中文字体管理器，支持动态缩放。"""
    
    _instance: Optional["FontManager"] = None
    _font_cache: dict = {}
    
    def __init__(self, font_path: str = None, base_size: int = 16):
        self._font_path = font_path
        self._base_size = base_size
        self._scale = 1.0
        self._default_font: Optional[pygame.font.Font] = None
        self._load_fonts()
    
    def _load_fonts(self):
        """加载字体文件。"""
        # 尝试加载中文字体
        if self._font_path and Path(self._font_path).exists():
            try:
                self._default_font = pygame.font.Font(self._font_path, self._base_size)
                return
            except Exception:
                pass
        
        # fallback 到系统字体
        try:
            self._default_font = pygame.font.SysFont("sans-serif", self._base_size)
        except Exception:
            self._default_font = pygame.font.Font(None, self._base_size)
    
    @classmethod
    def get_instance(cls, font_path: str = None, base_size: int = 16) -> "FontManager":
        """单例获取。"""
        if cls._instance is None:
            cls._instance = cls(font_path, base_size)
        return cls._instance
    
    @classmethod
    def reset(cls):
        """重置单例（用于测试）。"""
        cls._instance = None
    
    def set_scale(self, scale: float):
        """设置全局缩放系数。"""
        self._scale = max(0.5, min(3.0, scale))
        self._font_cache.clear()
    
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """获取指定大小的字体（带缓存）。"""
        scaled_size = int(size * self._scale)
        cache_key = (scaled_size, bold)
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        if self._default_font:
            try:
                font = pygame.font.Font(self._default_font.path, scaled_size)
            except AttributeError:
                font = pygame.font.Font(None, scaled_size)
        else:
            font = pygame.font.Font(None, scaled_size)
        
        self._font_cache[cache_key] = font
        return font
    
    def render_text(self, text: str, size: int, color: tuple, bold: bool = False) -> pygame.Surface:
        """渲染文字。"""
        font = self.get_font(size, bold)
        return font.render(text, True, color)
    
    @property
    def scale(self) -> float:
        return self._scale


# --- 触摸按钮组件 ---
class TouchButton:
    """可触摸的按钮组件。"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font_size: int = 14,
                 bg_color: tuple = (40, 40, 60),
                 text_color: tuple = (200, 200, 200),
                 hover_color: tuple = (60, 60, 100),
                 pressed_color: tuple = (80, 80, 140),
                 border_color: tuple = (100, 100, 140),
                 action: str = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.border_color = border_color
        self.action = action or text
        
        self._hovered = False
        self._pressed = False
        self._on_click = None
    
    def set_on_click(self, callback):
        """设置点击回调。"""
        self._on_click = callback
    
    def handle_touch(self, touch_pos: tuple, event_type: int) -> bool:
        """处理触摸事件，返回是否消耗了事件。"""
        x, y = touch_pos
        hit = self.rect.collidepoint(x, y)
        
        if event_type == pygame.FINGERDOWN:
            self._pressed = hit
            self._hovered = hit
            if hit and self._on_click:
                self._on_click()
            return hit
        
        elif event_type == pygame.FINGERMOTION:
            self._hovered = hit
            return False
        
        elif event_type == pygame.FINGERUP:
            was_pressed = self._pressed
            self._pressed = False
            if was_pressed and hit and self._on_click:
                self._on_click()
            return hit
        
        return False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染按钮。"""
        # 背景
        if self._pressed:
            color = self.pressed_color
        elif self._hovered:
            color = self.hover_color
        else:
            color = self.bg_color
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # 文字
        fm = FontManager.get_instance()
        txt_surf = fm.render_text(self.text, self.font_size, self.text_color)
        screen.blit(txt_surf, (
            self.rect.centerx - txt_surf.get_width() // 2,
            self.rect.centery - txt_surf.get_height() // 2
        ))
    
    def reset_state(self):
        """重置按钮状态。"""
        self._hovered = False
        self._pressed = False


# --- 进度条组件 ---
class ProgressBar:
    """可缩放的进度条。"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 bg_color: tuple = (40, 40, 40),
                 fill_color: tuple = (200, 50, 50),
                 border_color: tuple = (80, 80, 80)):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.value = 1.0
        self.max_value = 1.0
    
    def set_value(self, value: float, maximum: float):
        """设置进度值。"""
        self.max_value = max(0.01, maximum)
        self.value = max(0, min(value, self.max_value))
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染进度条。"""
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        ratio = self.value / self.max_value
        fill_width = int(self.rect.width * ratio)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.fill_color, fill_rect)
        
        pygame.draw.rect(screen, self.border_color, self.rect, 1)
