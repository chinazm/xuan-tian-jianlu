#!/usr/bin/env python3
"""生成中国风修仙Tileset (32x32 像素, 10列×8行 = 80 tiles)."""
from PIL import Image, ImageDraw
import math
import os

TILE = 32
COLS = 10
ROWS = 8
TILESET_W = TILE * COLS  # 320
TILESET_H = TILE * ROWS  # 256
OUTDIR = os.path.join(os.path.dirname(__file__), 'assets', 'tiles')
os.makedirs(OUTDIR, exist_ok=True)

# 中国风配色
C = {
    # 地面
    "grass":      (72, 133, 45),
    "grass_lt":   (90, 155, 60),
    "grass_dk":   (50, 100, 30),
    "dirt":       (158, 117, 65),
    "dirt_lt":    (180, 140, 85),
    "dirt_dk":    (130, 95, 50),
    "stone":      (130, 130, 135),
    "stone_lt":   (160, 160, 165),
    "stone_dk":   (95, 95, 100),
    "stone_path": (145, 140, 130),
    "stone_plt":  (170, 165, 155),
    "stone_pdk":  (115, 110, 100),
    # 水
    "water":      (40, 100, 160),
    "water_lt":   (60, 130, 190),
    "water_dk":   (25, 70, 120),
    "water_hl":   (90, 160, 210),
    # 竹
    "bamboo":     (55, 140, 55),
    "bamboo_lt":  (80, 170, 80),
    "bamboo_dk":  (35, 100, 35),
    "bamboo_hl":  (110, 200, 100),
    # 建筑
    "wall_white": (230, 225, 215),
    "wall_lt":    (245, 240, 230),
    "wall_dk":    (210, 200, 190),
    "wood":       (140, 85, 45),
    "wood_lt":    (170, 110, 60),
    "wood_dk":    (100, 60, 30),
    "roof":       (180, 50, 40),
    "roof_lt":    (210, 75, 60),
    "roof_dk":    (140, 35, 28),
    "pillar_red": (170, 40, 35),
    "pillar_lt":  (200, 60, 50),
    "pillar_dk":  (130, 25, 20),
    "gold":       (210, 180, 50),
    "gold_dk":    (170, 140, 30),
    # 装饰
    "lantern":    (210, 50, 40),
    "lantern_lt": (240, 80, 60),
    "stone_lion": (140, 135, 130),
    "stone_ls":   (165, 160, 155),
    "stone_ld":   (110, 105, 100),
    "flower_r":   (220, 60, 60),
    "flower_p":   (200, 80, 180),
    "flower_y":   (230, 200, 50),
    "leaf":       (60, 150, 70),
    "leaf_lt":    (85, 180, 90),
    # 桥
    "bridge":     (170, 120, 60),
    "bridge_lt":  (200, 150, 80),
    "bridge_dk":  (140, 95, 45),
    # 台阶
    "step":       (160, 155, 145),
    "step_lt":    (185, 180, 170),
    "step_dk":    (135, 130, 120),
    # 山石
    "rock":       (100, 100, 95),
    "rock_lt":    (130, 125, 120),
    "rock_dk":    (75, 75, 70),
    "moss":       (65, 120, 50),
    # 特殊
    "void":       (30, 30, 35),
    "dark":       (50, 50, 55),
}

def tile(draw_obj, col, row):
    """Get drawing context for a specific tile."""
    return draw_obj

def draw_grass(d, x, y):
    """草地 - 带纹理."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    d.rectangle([x, y, x+31, y+31], outline=C["grass_dk"])
    # 小草纹理
    for _ in range(8):
        gx = x + (hash(str(_)) % 28) + 2
        gy = y + (hash(str(_+10)) % 28) + 2
        d.rectangle([gx, gy, gx+1, gy+3], fill=C["grass_lt"])

def draw_dirt(d, x, y):
    """泥土 - 带颗粒感."""
    d.rectangle([x, y, x+31, y+31], fill=C["dirt"])
    d.rectangle([x, y, x+31, y+31], outline=C["dirt_dk"])
    for _ in range(6):
        dx = x + (hash(str(_+20)) % 28) + 2
        dy = y + (hash(str(_+30)) % 28) + 2
        d.point((dx, dy), fill=C["dirt_lt"])

def draw_stone_path(d, x, y):
    """青石板路."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    d.rectangle([x, y, x+31, y+31], outline=C["stone_pdk"])
    # 石板缝隙
    d.line([(x+15, y), (x+15, y+31)], fill=C["stone_pdk"])
    d.line([(x, y+15), (x+31, y+15)], fill=C["stone_pdk"])
    # 磨损效果
    d.point((x+8, y+8), fill=C["stone_plt"])
    d.point((x+23, y+20), fill=C["stone_plt"])

def draw_stone_path_h(d, x, y):
    """青石板路横向."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    d.line([(x, y), (x, y+31)], fill=C["stone_pdk"])
    d.line([(x+31, y), (x+31, y+31)], fill=C["stone_pdk"])
    d.line([(x, y+15), (x+31, y+15)], fill=C["stone_pdk"])
    d.point((x+10, y+10), fill=C["stone_plt"])

def draw_stone_path_v(d, x, y):
    """青石板路纵向."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    d.line([(x, y), (x+31, y)], fill=C["stone_pdk"])
    d.line([(x, y+31), (x+31, y+31)], fill=C["stone_pdk"])
    d.line([(x+15, y), (x+15, y+31)], fill=C["stone_pdk"])
    d.point((x+20, y+12), fill=C["stone_plt"])

def draw_water(d, x, y):
    """水面 - 带波纹."""
    d.rectangle([x, y, x+31, y+31], fill=C["water"])
    # 波纹
    for i in range(3):
        wy = y + 6 + i * 8
        d.line([(x+3, wy), (x+12, wy-1)], fill=C["water_hl"])
        d.line([(x+16, wy+1), (x+28, wy)], fill=C["water_lt"])

def draw_water_edge(d, x, y):
    """水边 - 与草交界."""
    d.rectangle([x, y, x+31, y+15], fill=C["water"])
    d.rectangle([x, y+16, x+31, y+31], fill=C["grass"])
    d.line([(x, y+15), (x+31, y+15)], fill=C["water_dk"])
    # 水花
    d.point((x+8, y+15), fill=C["water_hl"])
    d.point((x+22, y+14), fill=C["water_hl"])

def draw_water_edge_bottom(d, x, y):
    """水边 - 下."""
    d.rectangle([x, y, x+31, y+15], fill=C["grass"])
    d.rectangle([x, y+16, x+31, y+31], fill=C["water"])
    d.line([(x, y+16), (x+31, y+16)], fill=C["water_dk"])

def draw_bamboo(d, x, y):
    """竹林 - 密集竹子."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    # 竹竿
    d.rectangle([x+6, y, x+8, y+31], fill=C["bamboo"])
    d.rectangle([x+6, y, x+7, y+31], fill=C["bamboo_hl"])
    d.rectangle([x+20, y+5, x+22, y+31], fill=C["bamboo_dk"])
    d.rectangle([x+20, y+5, x+21, y+31], fill=C["bamboo_lt"])
    # 竹节
    d.rectangle([x+5, y+10, x+9, y+12], fill=C["bamboo_dk"])
    d.rectangle([x+5, y+22, x+9, y+24], fill=C["bamboo_dk"])
    d.rectangle([x+19, y+15, x+23, y+17], fill=C["bamboo"])
    # 竹叶
    d.rectangle([x+8, y+8, x+14, y+10], fill=C["leaf"])
    d.rectangle([x+22, y+12, x+28, y+14], fill=C["leaf_lt"])
    d.rectangle([x+4, y+20, x+10, y+22], fill=C["leaf"])
    d.rectangle([x+22, y+24, x+28, y+26], fill=C["leaf"])

def draw_bamboo_thick(d, x, y):
    """茂密竹林."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass_dk"])
    for bx, by in [(4, 0), (14, 3), (24, 1), (9, 8), (19, 6)]:
        d.rectangle([x+bx, y+by, x+bx+3, y+31], fill=C["bamboo"])
        d.rectangle([x+bx, y+by, x+bx+1, y+31], fill=C["bamboo_hl"])
    for lx, ly in [(7, 5), (17, 8), (3, 15), (27, 12), (12, 20), (22, 22)]:
        d.rectangle([x+lx, y+ly, x+lx+6, y+ly+2], fill=C["leaf"])
        d.rectangle([x+lx, y+ly, x+lx+3, y+ly+2], fill=C["leaf_lt"])

def draw_pond(d, x, y):
    """小池塘."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    d.ellipse([x+4, y+4, x+27, y+27], fill=C["water"])
    d.ellipse([x+4, y+4, x+27, y+27], outline=C["dirt"])
    # 水面波纹
    d.line([(x+10, y+12), (x+20, y+11)], fill=C["water_hl"])
    d.line([(x+8, y+20), (x+18, y+21)], fill=C["water_lt"])
    # 荷叶
    d.ellipse([x+18, y+6, x+24, y+10], fill=C["leaf"])

def draw_rock(d, x, y):
    """山石."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    # 石头
    d.polygon([(x+4, y+28), (x+8, y+10), (x+14, y+6), (x+22, y+8), (x+28, y+20), (x+28, y+28)], fill=C["rock"])
    d.polygon([(x+4, y+28), (x+8, y+10), (x+14, y+6), (x+22, y+8), (x+28, y+20), (x+28, y+28)], outline=C["rock_dk"])
    d.line([(x+10, y+12), (x+20, y+14)], fill=C["rock_lt"])
    # 苔藓
    d.rectangle([x+6, y+22, x+12, y+24], fill=C["moss"])
    d.rectangle([x+16, y+24, x+22, y+26], fill=C["moss"])

def draw_flower_patch(d, x, y):
    """花丛."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    for fx, fy, fc in [(6, 10, C["flower_r"]), (16, 8, C["flower_p"]), (24, 14, C["flower_y"]),
                        (10, 20, C["flower_y"]), (20, 22, C["flower_r"])]:
        d.rectangle([x+fx, y+fy, x+fx+2, y+fy+4], fill=C["leaf"])
        d.ellipse([x+fx-1, y+fy-2, x+fx+3, y+fy+2], fill=fc)

def draw_wall(d, x, y):
    """白墙 - 传统建筑墙面."""
    d.rectangle([x, y, x+31, y+31], fill=C["wall_white"])
    d.rectangle([x, y, x+31, y+2], fill=C["wall_dk"])
    d.rectangle([x, y, x+2, y+31], fill=C["wall_dk"])
    d.rectangle([x+29, y, x+31, y+31], fill=C["wall_lt"])
    # 砖纹
    d.line([(x, y+10), (x+31, y+10)], fill=C["wall_dk"])
    d.line([(x, y+20), (x+31, y+20)], fill=C["wall_dk"])
    d.line([(x+15, y+10), (x+15, y+20)], fill=C["wall_dk"])

def draw_wall_corner(d, x, y):
    """墙角."""
    d.rectangle([x, y, x+31, y+31], fill=C["wall_white"])
    d.rectangle([x, y, x+31, y+31], outline=C["wall_dk"])
    # 砖纹
    d.line([(x+15, y), (x+15, y+31)], fill=C["wall_dk"])
    d.line([(x, y+10), (x+31, y+10)], fill=C["wall_dk"])
    d.line([(x, y+20), (x+31, y+20)], fill=C["wall_dk"])

def draw_wood_floor(d, x, y):
    """木地板 - 回廊."""
    d.rectangle([x, y, x+31, y+31], fill=C["wood"])
    d.line([(x, y+7), (x+31, y+7)], fill=C["wood_dk"])
    d.line([(x, y+15), (x+31, y+15)], fill=C["wood_dk"])
    d.line([(x, y+23), (x+31, y+23)], fill=C["wood_dk"])
    d.line([(x, y+7), (x+31, y+7)], fill=C["wood_lt"])

def draw_door(d, x, y):
    """木门 - 传统对开门."""
    d.rectangle([x, y, x+31, y+31], fill=C["wood"])
    d.rectangle([x+1, y+1, x+14, y+30], fill=C["wood_lt"])
    d.rectangle([x+16, y+1, x+29, y+30], fill=C["wood_dk"])
    d.rectangle([x+15, y, x+16, y+31], fill=C["wood_dk"])
    # 门钉
    d.point((x+8, y+15), fill=C["gold"])
    d.point((x+22, y+15), fill=C["gold"])
    # 门环
    d.ellipse([x+6, y+10, x+10, y+14], fill=C["gold_dk"])
    d.ellipse([x+20, y+10, x+24, y+14], fill=C["gold_dk"])

def draw_pillar(d, x, y):
    """红柱 - 传统建筑柱子."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    d.rectangle([x+10, y, x+21, y+31], fill=C["pillar_red"])
    d.rectangle([x+10, y, x+13, y+31], fill=C["pillar_lt"])
    d.rectangle([x+19, y, x+21, y+31], fill=C["pillar_dk"])
    # 柱础
    d.rectangle([x+8, y+28, x+23, y+31], fill=C["stone"])
    d.rectangle([x+8, y+28, x+23, y+29], fill=C["stone_lt"])
    # 柱头
    d.rectangle([x+7, y, x+24, y+3], fill=C["gold"])
    d.rectangle([x+7, y, x+24, y+1], fill=C["gold_dk"])

def draw_roof(d, x, y):
    """屋檐顶."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 瓦片
    for rx in range(x, x+32, 8):
        d.polygon([(rx, y+16), (rx+4, y), (rx+8, y+16)], fill=C["roof"])
        d.polygon([(rx, y+16), (rx+4, y), (rx+8, y+16)], outline=C["roof_dk"])
        d.line([(rx+4, y+2), (rx+4, y+12)], fill=C["roof_lt"])
    # 屋檐边
    d.rectangle([x, y+16, x+31, y+18], fill=C["roof_dk"])
    # 瓦当
    d.ellipse([x+14, y+16, x+18, y+20], fill=C["gold"])

def draw_lantern(d, x, y):
    """红灯笼."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 杆
    d.rectangle([x+15, y, x+17, y+12], fill=C["wood_dk"])
    # 灯笼
    d.ellipse([x+10, y+10, x+22, y+26], fill=C["lantern"])
    d.ellipse([x+10, y+10, x+22, y+26], outline=C["pillar_dk"])
    d.ellipse([x+12, y+12, x+18, y+20], fill=C["lantern_lt"])
    # 穗子
    d.rectangle([x+14, y+26, x+18, y+30], fill=C["gold"])
    d.rectangle([x+15, y+26, x+16, y+30], fill=C["gold_dk"])
    # 顶部装饰
    d.rectangle([x+12, y+8, x+20, y+11], fill=C["gold"])

def draw_stone_lion(d, x, y):
    """石狮子."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 底座
    d.rectangle([x+4, y+24, x+27, y+30], fill=C["stone_ls"])
    d.rectangle([x+4, y+24, x+27, y+25], fill=C["stone_lion"])
    # 身体
    d.rectangle([x+8, y+14, x+22, y+24], fill=C["stone_lion"])
    d.rectangle([x+8, y+14, x+22, y+15], fill=C["stone_ls"])
    # 头
    d.rectangle([x+10, y+6, x+20, y+14], fill=C["stone_lion"])
    d.rectangle([x+10, y+6, x+20, y+7], fill=C["stone_ls"])
    # 眼睛
    d.point((x+13, y+10), fill=C["stone_ld"])
    d.point((x+18, y+10), fill=C["stone_ld"])
    # 鬃毛
    d.rectangle([x+8, y+6, x+10, y+12], fill=C["stone_dk"])
    d.rectangle([x+20, y+6, x+22, y+12], fill=C["stone_dk"])

def draw_bridge(d, x, y):
    """石桥."""
    d.rectangle([x, y, x+31, y+31], fill=C["bridge"])
    # 桥面石板
    d.rectangle([x+2, y+4, x+29, y+12], fill=C["bridge_lt"])
    d.rectangle([x+2, y+18, x+29, y+26], fill=C["bridge_lt"])
    # 栏杆
    d.rectangle([x+1, y+1, x+3, y+31], fill=C["bridge_dk"])
    d.rectangle([x+28, y+1, x+30, y+31], fill=C["bridge_dk"])
    # 栏板
    d.rectangle([x+4, y+8, x+6, y+10], fill=C["stone"])
    d.rectangle([x+12, y+8, x+14, y+10], fill=C["stone"])
    d.rectangle([x+20, y+8, x+22, y+10], fill=C["stone"])
    d.rectangle([x+4, y+22, x+6, y+24], fill=C["stone"])
    d.rectangle([x+12, y+22, x+14, y+24], fill=C["stone"])
    d.rectangle([x+20, y+22, x+24, y+24], fill=C["stone"])

def draw_steps(d, x, y):
    """石阶."""
    d.rectangle([x, y, x+31, y+10], fill=C["step_lt"])
    d.rectangle([x, y+10, x+31, y+20], fill=C["step"])
    d.rectangle([x, y+20, x+31, y+31], fill=C["step_dk"])
    # 台阶线
    d.line([(x, y+10), (x+31, y+10)], fill=C["step_dk"])
    d.line([(x, y+20), (x+31, y+20)], fill=C["stone_dk"])
    d.line([(x, y+11), (x+31, y+11)], fill=C["step_lt"])
    d.line([(x, y+21), (x+31, y+21)], fill=C["step"])

def draw_well(d, x, y):
    """古井."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 井口
    d.ellipse([x+8, y+8, x+24, y+24], fill=C["dark"])
    d.ellipse([x+8, y+8, x+24, y+24], outline=C["stone"])
    d.ellipse([x+10, y+10, x+22, y+22], fill=C["dark"])
    # 井台
    d.ellipse([x+6, y+6, x+26, y+26], outline=C["stone_dk"])
    # 苔藓
    d.point((x+8, y+10), fill=C["moss"])
    d.point((x+22, y+20), fill=C["moss"])

def draw_treasure(d, x, y):
    """宝箱/箱子."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    d.rectangle([x+6, y+14, x+24, y+26], fill=C["wood"])
    d.rectangle([x+6, y+14, x+24, y+18], fill=C["wood_lt"])
    d.rectangle([x+6, y+14, x+24, y+15], fill=C["wood_lt"])
    # 锁扣
    d.rectangle([x+13, y+18, x+17, y+22], fill=C["gold"])
    d.rectangle([x+14, y+19, x+16, y+21], fill=C["gold_dk"])

def draw_stone_table(d, x, y):
    """石桌."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 桌面
    d.ellipse([x+6, y+8, x+26, y+20], fill=C["stone"])
    d.ellipse([x+6, y+8, x+26, y+20], outline=C["stone_dk"])
    # 桌腿
    d.rectangle([x+10, y+20, x+13, y+28], fill=C["stone_dk"])
    d.rectangle([x+18, y+20, x+21, y+28], fill=C["stone_dk"])

def draw_fence(d, x, y):
    """竹篱笆."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    # 竖竹
    for fx in [2, 8, 14, 20, 26]:
        d.rectangle([x+fx, y+2, x+fx+4, y+28], fill=C["bamboo"])
        d.rectangle([x+fx, y+2, x+fx+2, y+28], fill=C["bamboo_hl"])
    # 横竹
    d.rectangle([x+2, y+8, x+30, y+10], fill=C["bamboo_dk"])
    d.rectangle([x+2, y+20, x+30, y+22], fill=C["bamboo_dk"])

def draw_gate(d, x, y):
    """牌坊/门楼."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 柱子
    d.rectangle([x+2, y+4, x+7, y+30], fill=C["pillar_red"])
    d.rectangle([x+2, y+4, x+4, y+30], fill=C["pillar_lt"])
    d.rectangle([x+24, y+4, x+29, y+30], fill=C["pillar_red"])
    d.rectangle([x+24, y+4, x+26, y+30], fill=C["pillar_lt"])
    # 横梁
    d.rectangle([x+2, y+4, x+29, y+8], fill=C["roof"])
    d.rectangle([x+2, y+4, x+29, y+5], fill=C["roof_lt"])
    # 匾额
    d.rectangle([x+10, y+8, x+20, y+12], fill=C["gold"])
    d.rectangle([x+10, y+8, x+20, y+9], fill=C["gold_dk"])
    # 瓦顶
    d.rectangle([x, y, x+31, y+4], fill=C["roof"])
    d.rectangle([x+1, y, x+30, y+1], fill=C["roof_lt"])

def draw_moon_gate(d, x, y):
    """月亮门."""
    d.rectangle([x, y, x+31, y+31], fill=C["wall_white"])
    # 门洞
    d.ellipse([x+8, y+4, x+24, y+30], fill=C["dark"])
    d.ellipse([x+8, y+4, x+24, y+30], outline=C["stone_dk"])
    # 门框装饰
    d.ellipse([x+9, y+5, x+23, y+29], outline=C["wall_dk"])

def draw_altar(d, x, y):
    """祭坛/炼丹炉."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 基座
    d.rectangle([x+4, y+20, x+27, y+30], fill=C["stone"])
    d.rectangle([x+4, y+20, x+27, y+22], fill=C["stone_lt"])
    # 炉身
    d.rectangle([x+8, y+10, x+22, y+20], fill=C["rock_dk"])
    d.rectangle([x+8, y+10, x+22, y+12], fill=C["rock"])
    # 炉口
    d.ellipse([x+10, y+8, x+20, y+12], fill=C["dark"])
    # 火焰
    d.point((x+14, y+6), fill=C["flower_r"])
    d.point((x+16, y+7), fill=C["flower_y"])
    d.point((x+15, y+5), fill=C["flower_r"])

def draw_torch(d, x, y):
    """火把/壁灯."""
    d.rectangle([x, y, x+31, y+31], fill=C["stone_path"])
    # 杆
    d.rectangle([x+14, y+10, x+18, y+30], fill=C["wood_dk"])
    # 火把头
    d.ellipse([x+11, y+4, x+21, y+12], fill=C["flower_y"])
    d.ellipse([x+12, y+6, x+20, y+10], fill=C["flower_r"])
    d.ellipse([x+14, y+7, x+18, y+9], fill=C["flower_r"])

def draw_void(d, x, y):
    """不可通行区域."""
    d.rectangle([x, y, x+31, y+31], fill=C["void"])

def draw_mountain(d, x, y):
    """山石远景."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    d.polygon([(x+2, y+31), (x+8, y+8), (x+16, y+2), (x+24, y+10), (x+30, y+31)], fill=C["rock"])
    d.polygon([(x+2, y+31), (x+8, y+8), (x+16, y+2), (x+24, y+10), (x+30, y+31)], outline=C["rock_dk"])
    d.line([(x+12, y+6), (x+20, y+12)], fill=C["rock_lt"])
    # 云雾
    d.ellipse([x+4, y+20, x+14, y+26], fill=C["wall_white"])
    d.ellipse([x+18, y+22, x+28, y+28], fill=C["wall_white"])

def draw_garden_rock(d, x, y):
    """太湖石/园林石."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    # 石头主体
    d.polygon([(x+6, y+30), (x+4, y+16), (x+8, y+6), (x+16, y+4), (x+24, y+8), (x+28, y+18), (x+26, y+30)], fill=C["rock"])
    d.polygon([(x+6, y+30), (x+4, y+16), (x+8, y+6), (x+16, y+4), (x+24, y+8), (x+28, y+18), (x+26, y+30)], outline=C["rock_dk"])
    # 纹理
    d.line([(x+10, y+10), (x+18, y+14)], fill=C["rock_lt"])
    d.line([(x+14, y+8), (x+22, y+16)], fill=C["rock_lt"])
    # 苔藓
    d.rectangle([x+6, y+26, x+14, y+28], fill=C["moss"])
    d.rectangle([x+18, y+24, x+24, y+26], fill=C["moss"])

# Tile mapping: (col, row) -> draw function
TILES = {
    (0, 0): draw_grass,       # 1 - 草地
    (1, 0): draw_dirt,        # 2 - 泥土
    (2, 0): draw_stone_path,  # 3 - 青石板路(十字缝)
    (3, 0): draw_stone_path_h,# 4 - 青石板路(横缝)
    (4, 0): draw_stone_path_v,# 5 - 青石板路(纵缝)
    (5, 0): draw_water,       # 6 - 水面
    (6, 0): draw_water_edge,  # 7 - 水边(上水)
    (7, 0): draw_water_edge_bottom, # 8 - 水边(下水)
    (8, 0): draw_bamboo,      # 9 - 竹林
    (9, 0): draw_bamboo_thick,# 10 - 茂密竹林
    
    (0, 1): draw_pond,        # 11 - 小池塘
    (1, 1): draw_rock,        # 12 - 山石
    (2, 1): draw_flower_patch,# 13 - 花丛
    (3, 1): draw_wall,        # 14 - 白墙
    (4, 1): draw_wall_corner, # 15 - 墙角
    (5, 1): draw_wood_floor,  # 16 - 木地板
    (6, 1): draw_door,        # 17 - 木门
    (7, 1): draw_pillar,      # 18 - 红柱
    (8, 1): draw_roof,        # 19 - 屋檐瓦片
    (9, 1): draw_lantern,     # 20 - 红灯笼
    
    (0, 2): draw_stone_lion,  # 21 - 石狮子
    (1, 2): draw_bridge,      # 22 - 石桥
    (2, 2): draw_steps,       # 23 - 石阶
    (3, 2): draw_well,        # 24 - 古井
    (4, 2): draw_treasure,    # 25 - 宝箱
    (5, 2): draw_stone_table, # 26 - 石桌
    (6, 2): draw_fence,       # 27 - 竹篱笆
    (7, 2): draw_gate,        # 28 - 牌坊/门楼
    (8, 2): draw_moon_gate,   # 29 - 月亮门
    (9, 2): draw_altar,       # 30 - 炼丹炉
    
    (0, 3): draw_torch,       # 31 - 火把
    (1, 3): draw_void,        # 32 - 不可通行
    (2, 3): draw_mountain,    # 33 - 山石远景
    (3, 3): draw_garden_rock, # 34 - 太湖石
    
    # Fill remaining with grass variations
}

# Additional grass/ground variations for fill
def draw_grass2(d, x, y):
    """草地变体."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass"])
    d.rectangle([x, y, x+31, y+31], outline=C["grass_dk"])
    for _ in range(10):
        gx = x + (hash(str(_+50)) % 28) + 2
        gy = y + (hash(str(_+60)) % 28) + 2
        d.rectangle([gx, gy, gx+2, gy+3], fill=C["grass_lt"])

def draw_grass3(d, x, y):
    """草地变体3."""
    d.rectangle([x, y, x+31, y+31], fill=C["grass_dk"])
    d.rectangle([x, y, x+31, y+31], outline=C["grass"])
    for _ in range(6):
        gx = x + (hash(str(_+70)) % 28) + 2
        gy = y + (hash(str(_+80)) % 28) + 2
        d.rectangle([gx, gy, gx+1, gy+4], fill=C["moss"])

FILL_TILES = [draw_grass2, draw_grass3, draw_dirt]

def main():
    sheet = Image.new("RGBA", (TILESET_W, TILESET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    
    tile_idx = 0
    for row in range(ROWS):
        for col in range(COLS):
            tile_idx += 1
            x = col * TILE
            y = row * TILE
            
            if (col, row) in TILES:
                TILES[(col, row)](draw, x, y)
            else:
                # Fill remaining with grass variants
                fill_fn = FILL_TILES[tile_idx % len(FILL_TILES)]
                fill_fn(draw, x, y)
    
    path = os.path.join(OUTDIR, 'tileset.png')
    sheet.save(path, "PNG")
    print(f"Saved {path} ({TILESET_W}x{TILESET_H}, {COLS*ROWS} tiles)")
    
    # Print tile mapping
    print("\nTile ID mapping:")
    idx = 0
    for row in range(ROWS):
        for col in range(COLS):
            idx += 1
            name = ""
            for (c, r), fn in TILES.items():
                if c == col and r == row:
                    name = fn.__doc__ or ""
                    break
            if not name:
                name = "grass variant"
            print(f"  Tile {idx:2d} ({col},{row}): {name}")

if __name__ == "__main__":
    main()
