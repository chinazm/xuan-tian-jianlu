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
    bg_color = tuple(win_cfg.get("background_color", [20, 20, 30]))

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill(bg_color)
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
