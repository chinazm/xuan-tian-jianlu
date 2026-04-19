"""玄天剑录 - 像素仙侠RPG
核心引擎与游戏内容完全分离（外部结构架构）。
"""
import sys
import os
import pygame
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

# --- 设计分辨率 (虚拟画布) ---
VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600


def load_settings() -> dict:
    """加载配置文件，带错误处理。"""
    settings_path = BASE_DIR / "config" / "settings.json"
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到配置文件 {settings_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件 JSON 格式错误: {e}")
        sys.exit(1)


def is_android() -> bool:
    """检测是否在 Android 环境运行。"""
    try:
        import android  # noqa: F401
        return True
    except (ImportError, RuntimeError, OSError):
        return False


def main():
    try:
        settings = load_settings()
    except Exception as e:
        import traceback
        print(f"[FATAL] load_settings failed: {e}")
        traceback.print_exc()
        return
    
    win_cfg = settings.get("window", {})
    title = win_cfg.get("title", "玄天剑录")
    target_fps = win_cfg.get("fps", 60)
    
    # Android 环境检测与适配
    android_env = is_android()
    print(f"[main] Android 环境: {android_env}")
    
    if android_env:
        # Android: 使用系统分辨率，全屏
        # 先尝试安全初始化音频，某些 Android 设备不支持 pre_init 特定参数
        try:
            pygame.mixer.pre_init(44100, -16, 2, 4096)
        except Exception as e:
            print(f"[main] pre_init 失败，尝试默认: {e}")
            try:
                pygame.mixer.pre_init()
            except Exception as e2:
                print(f"[main] pre_init 默认也失败，跳过音频: {e2}")
        
        # Android 14+ 需要在 pygame.init() 前设置环境变量
        os.environ["SDL_VIDEO_FULLSCREEN"] = "1"
        os.environ["SDL_HINT_ANDROID_BLOCK_ON_RESUME_PAUSE"] = "0"
        
        try:
            pygame.init()
            print("[main] pygame.init() 成功")
        except Exception as e:
            print(f"[FATAL] pygame.init() 失败: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 检查音频是否初始化成功
        if not pygame.mixer.get_init():
            print("[main] 警告: pygame.mixer 未初始化，音频将不可用")
        # 安全获取屏幕尺寸（某些 Android 设备 Info() 可能异常）
        try:
            info = pygame.display.Info()
            if info is None or info.current_w is None or info.current_h is None:
                raise ValueError("Info() returned None")
            screen_width, screen_height = info.current_w, info.current_h
            print(f"[main] 屏幕分辨率: {screen_width}x{screen_height}")
        except Exception as e:
            print(f"[main] display.Info() 失败，使用默认分辨率: {e}")
            screen_width, screen_height = 1920, 1080
        # 移除 HWSURFACE/DOUBLEBUF/SCALED/FULLSCREEN（SDL2 已废弃，Android 14+ 上 FULLSCREEN 会崩溃）
        # Android 默认全屏，不需要显式设置 FULLSCREEN
        flags = 0
    else:
        # 桌面: 使用设计分辨率
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        screen_width = win_cfg.get("width", VIRTUAL_WIDTH)
        screen_height = win_cfg.get("height", VIRTUAL_HEIGHT)
        flags = pygame.RESIZABLE
    
    # 创建物理屏幕
    try:
        screen = pygame.display.set_mode((screen_width, screen_height), flags)
        print(f"[main] set_mode 成功: {screen_width}x{screen_height}")
    except Exception as e:
        print(f"[FATAL] set_mode 失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        pygame.display.set_caption(title)
        clock = pygame.time.Clock()

        # 创建虚拟画布 (内部渲染目标)
        # 游戏逻辑和所有 UI 都在这个尺寸下绘制，然后缩放
        virtual_canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        
        # 计算缩放系数
        scale_x = screen_width / VIRTUAL_WIDTH
        scale_y = screen_height / VIRTUAL_HEIGHT
        # 保持宽高比的缩放 (Letterboxing)
        scale = min(scale_x, scale_y)
        
        # 计算居中偏移
        offset_x = (screen_width - VIRTUAL_WIDTH * scale) // 2
        offset_y = (screen_height - VIRTUAL_HEIGHT * scale) // 2

        # 初始化游戏场景
        from core.config import GameConfig
        from core.game import GameScene

        config = GameConfig()
        # 传入虚拟分辨率给游戏逻辑
        config.window.width = VIRTUAL_WIDTH
        config.window.height = VIRTUAL_HEIGHT
        config.window.fps = target_fps
        config.window.title = title

        print("[main] 创建 GameScene...")
        scene = GameScene(config, room_id="ch01_qingshi_town", base_dir=BASE_DIR)
        print("[main] GameScene 创建成功")
        scene.on_enter()

        running = True
        try:
            while running:
                # 计算 dt
                dt = clock.tick(target_fps) / 1000.0

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    # 将鼠标/触摸坐标转换为虚拟画布坐标
                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                        mx, my = event.pos
                        vx = int((mx - offset_x) / scale)
                        vy = int((my - offset_y) / scale)
                        # 更新事件坐标以便后续逻辑处理 (如果支持鼠标)
                        if hasattr(event, 'dict'):
                            event.dict['x'] = vx
                            event.dict['y'] = vy
                    
                    scene.handle_event(event)

                scene.update(dt)
                
                # 1. 渲染到虚拟画布
                scene.render(virtual_canvas)
                
                # 2. 缩放并绘制到物理屏幕（smoothscale 在高分辨率 Android 上极易 OOM）
                screen.fill((0, 0, 0))  # 黑边填充
                try:
                    scaled_surface = pygame.transform.scale(virtual_canvas, (int(VIRTUAL_WIDTH * scale), int(VIRTUAL_HEIGHT * scale)))
                except Exception as e:
                    # fallback：直接 blit 不缩放
                    print(f"[main] scale 失败，使用原始尺寸: {e}")
                    scaled_surface = virtual_canvas
                screen.blit(scaled_surface, (offset_x, offset_y))
                
                pygame.display.flip()
        finally:
            scene.on_exit()
            pygame.quit()
    except Exception as e:
        print(f"[FATAL] 游戏运行异常: {e}")
        import traceback
        traceback.print_exc()
        try:
            pygame.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
