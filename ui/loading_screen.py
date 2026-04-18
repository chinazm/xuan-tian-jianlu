"""Loading 界面：进度条 + 提示文字。"""
import pygame
from ui.base_ui import FontManager, ProgressBar


class LoadingScreen:
    """加载界面。"""
    
    TIPS = [
        "修炼之路，漫漫其修远...",
        "御剑乘风，逍遥天地间。",
        "灵气汇聚，突破在即。",
        "斩妖除魔，证道长生。",
        "点击屏幕任意位置继续。",
    ]
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self._scale = min(width / 800, height / 600)
        
        self.fm = FontManager.get_instance()
        self.fm.set_scale(self._scale)
        
        # 进度条
        bar_width = int(min(width * 0.6, 400 * self._scale))
        bar_height = int(16 * self._scale)
        self._progress_bar = ProgressBar(
            (width - bar_width) // 2,
            int(height * 0.6),
            bar_width, bar_height,
            fill_color=(100, 150, 200)
        )
        
        # 提示文字
        self._tip_text = self.TIPS[0]
        self._tip_pos = (width // 2, int(height * 0.7))
        
        self._progress = 0.0
        self._loading_text = "加载中..."
        self._visible = False
    
    def start(self):
        """开始加载。"""
        self._progress = 0.0
        self._visible = True
    
    def update(self, progress: float):
        """更新进度 (0.0 ~ 1.0)。"""
        self._progress = max(0, min(1.0, progress))
        if self._progress >= 1.0:
            self._loading_text = "准备就绪！"
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染加载界面。"""
        if not self._visible:
            return
        
        # 全屏背景
        screen.fill((15, 15, 25))
        
        # 标题
        title = self.fm.render_text("玄天剑录", 28, (255, 215, 0), bold=True)
        screen.blit(title, (self.width // 2 - title.get_width() // 2, int(self.height * 0.25)))
        
        # 进度条
        self._progress_bar.set_value(self._progress, 1.0)
        self._progress_bar.render(screen)
        
        # 进度文字
        pct_text = self.fm.render_text(
            f"{self._loading_text} {int(self._progress * 100)}%",
            13, (180, 180, 180)
        )
        screen.blit(pct_text, (self.width // 2 - pct_text.get_width() // 2,
                              int(self.height * 0.65)))
        
        # 提示文字
        tip_surf = self.fm.render_text(self._tip_text, 12, (120, 120, 120))
        screen.blit(tip_surf, (self.width // 2 - tip_surf.get_width() // 2,
                              self._tip_pos[1]))
    
    def dismiss(self):
        """关闭加载界面。"""
        self._visible = False
    
    @property
    def is_visible(self) -> bool:
        return self._visible
