"""玄天剑录 - 像素仙侠RPG
核心引擎与游戏内容完全分离（外部结构架构）。
"""
import sys
import pygame
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


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


def main():
    settings = load_settings()
    win_cfg = settings.get("window", {})
    width = win_cfg.get("width", 800)
    height = win_cfg.get("height", 600)
    title = win_cfg.get("title", "玄天剑录")
    fps = win_cfg.get("fps", 60)

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    # 初始化游戏场景
    from core.config import GameConfig
    from core.game import GameScene

    config = GameConfig()
    config.window.width = width
    config.window.height = height
    config.window.fps = fps
    config.window.title = title

    scene = GameScene(config, room_id="sect_main")
    scene.on_enter()

    running = True
    while running:
        dt = clock.tick(fps) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene.handle_event(event)

        scene.update(dt)
        scene.render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
