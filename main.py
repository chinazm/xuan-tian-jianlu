"""玄天剑录 - 像素仙侠RPG
核心引擎与游戏内容完全分离（外部结构架构）。
"""
import pygame
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

def load_settings():
    settings_path = BASE_DIR / "config" / "settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    settings = load_settings()
    win_cfg = settings["window"]
    
    pygame.init()
    screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
    pygame.display.set_caption(win_cfg["title"])
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((20, 20, 30))
        pygame.display.flip()
        clock.tick(win_cfg["fps"])
    
    pygame.quit()

if __name__ == "__main__":
    main()
