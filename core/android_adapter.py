"""Android 系统适配器：通过 JNI 安全调用 Android 原生 API。"""
import os


class AndroidAdapter:
    """
    封装 Android 专属功能（震动、Wakelock）。
    在桌面端运行时，所有方法均为空操作 (No-op)。
    """

    def __init__(self):
        self._available = False
        self._activity = None
        self._context = None
        # 先检查是否在 p4a 环境
        if 'ANDROID_ARGUMENT' not in os.environ and 'ANDROID_APP_PATH' not in os.environ:
            print("[AndroidAdapter] 非 Android 环境，跳过 JNI 初始化")
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            self._activity = PythonActivity.mActivity
            self._context = Context
            self._available = True
            print("[AndroidAdapter] JNI 环境已初始化")
        except Exception as e:
            print(f"[AndroidAdapter] JNI 不可用 (安全跳过): {e}")

    def vibrate(self, duration_ms: int = 100):
        """触发设备震动。"""
        if not self._available:
            return
        try:
            from jnius import autoclass
            Vibrator = autoclass('android.os.Vibrator')
            vibrator = self._activity.getSystemService(self._context.VIBRATOR_SERVICE)
            # Android API 26+ 使用 VibrationEffect，但旧 API 仍兼容
            vibrator.vibrate(duration_ms)
        except Exception as e:
            print(f"[AndroidAdapter] Vibrate failed: {e}")

    def acquire_wakelock(self):
        """获取屏幕常亮锁 (WakeLock)。"""
        if not self._available:
            return
        try:
            from jnius import autoclass
            PowerManager = autoclass('android.os.PowerManager')
            pm = self._activity.getSystemService(self._context.POWER_SERVICE)
            self._wake_lock = pm.newWakeLock(
                PowerManager.SCREEN_BRIGHT_WAKE_LOCK,
                "XuanTianJianLu::GameWakelock"
            )
            self._wake_lock.acquire()
            print("[AndroidAdapter] Wakelock acquired")
        except Exception as e:
            print(f"[AndroidAdapter] WakeLock failed: {e}")

    def release_wakelock(self):
        """释放屏幕常亮锁。"""
        if not self._available:
            return
        try:
            if hasattr(self, '_wake_lock'):
                self._wake_lock.release()
                print("[AndroidAdapter] WakeLock released")
        except Exception as e:
            print(f"[AndroidAdapter] Release WakeLock failed: {e}")

    def is_android(self) -> bool:
        """检测是否在 Android 环境运行。"""
        return self._available
