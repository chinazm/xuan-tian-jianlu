"""性能配置与动态帧率调整。"""
import time


class PerformanceMonitor:
    """监控游戏性能指标。"""
    
    def __init__(self, window_size: int = 60):
        self._frame_times: list[float] = []
        self._window_size = window_size
        self._fps = 60.0
        self._last_update = 0.0
    
    def mark_frame(self, dt: float):
        """记录一帧耗时。"""
        self._frame_times.append(dt)
        if len(self._frame_times) > self._window_size:
            self._frame_times.pop(0)
    
    @property
    def fps(self) -> float:
        """计算当前平均 FPS。"""
        if not self._frame_times:
            return 60.0
        avg_dt = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / avg_dt if avg_dt > 0 else 60.0
    
    @property
    def frame_ms(self) -> float:
        """平均帧耗时 (ms)。"""
        if not self._frame_times:
            return 16.6
        return (sum(self._frame_times) / len(self._frame_times)) * 1000


class DynamicFPS:
    """动态帧率控制器。
    
    根据设备性能自动调整目标 FPS，防止低端机过热卡顿。
    """
    
    # 性能分级
    HIGH_PERF = 60
    MID_PERF = 45
    LOW_PERF = 30
    
    # 阈值 (ms)
    THRESHOLD_UP = 18    # < 18ms -> 60fps
    THRESHOLD_MID = 25   # < 25ms -> 45fps
    # > 25ms -> 30fps
    
    def __init__(self):
        self.target_fps = self.HIGH_PERF
        self._perf = PerformanceMonitor()
    
    def update(self, dt: float):
        """每帧调用，调整目标 FPS。"""
        self._perf.mark_frame(dt)
        
        # 避免频繁波动，每 0.5 秒检查一次
        now = time.time()
        if now - self._perf._last_update < 0.5:
            return
        
        self._perf._last_update = now
        avg_ms = self._perf.frame_ms
        
        if avg_ms < self.THRESHOLD_UP:
            self.target_fps = self.HIGH_PERF
        elif avg_ms < self.THRESHOLD_MID:
            self.target_fps = self.MID_PERF
        else:
            self.target_fps = self.LOW_PERF
