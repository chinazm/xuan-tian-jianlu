"""Android 系统适配器：安全调用 Android 原生 API (震动、Wakelock)。"""


class AndroidAdapter:
    """
    封装 Android 专属功能。
    在桌面端运行时，所有方法均为空操作 (No-op)。
    """

    def __init__(self):
        self._android = None
        try:
            import android
            self._android = android
            print("[AndroidAdapter] Android 环境已初始化")
        except ImportError:
            print("[AndroidAdapter] 运行于非 Android 环境 (桌面/模拟器)")

    def vibrate(self, duration_ms: int = 100):
        """
        触发设备震动。
        :param duration_ms: 震动持续时间 (毫秒)
        """
        if self._android:
            try:
                self._android.vibrator.vibrate(duration_ms)
            except Exception as e:
                print(f"[AndroidAdapter] Vibrate failed: {e}")

    def acquire_wakelock(self):
        """获取屏幕常亮锁 (WakeLock)。"""
        if self._android:
            try:
                # Pygame for Android 通常会自动保持唤醒，但显式获取更保险
                from android import power
                power.WakeLock(power.FULL_WAKE_LOCK)
                print("[AndroidAdapter] Wakelock acquired")
            except Exception as e:
                print(f"[AndroidAdapter] WakeLock failed: {e}")

    def release_wakelock(self):
        """释放屏幕常亮锁。"""
        if self._android:
            try:
                from android import power
                power.ReleaseWakeLock()
            except Exception as e:
                print(f"[AndroidAdapter] Release WakeLock failed: {e}")

    def is_android(self) -> bool:
        """检测是否在 Android 环境运行。"""
        return self._android is not None
