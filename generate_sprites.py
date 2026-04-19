#!/usr/bin/env python3
"""生成主角、竹妖、骷髅将军的像素精灵表 (128x128, 4方向×4帧, 32x32每帧)."""
from PIL import Image, ImageDraw
import math
import os

SPRITE_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'sprites')
FRAME_SIZE = 32
GRID = 4  # 4 directions × 4 frames
DIR_NAMES = ["down", "up", "left", "right"]

def make_canvas(w=FRAME_SIZE, h=FRAME_SIZE):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def draw_pixel(draw, x, y, color):
    draw.point((x, y), fill=color)

def draw_rect(draw, x, y, w, h, color):
    draw.rectangle([x, y, x+w-1, y+h-1], fill=color)

def draw_ellipse(draw, x0, y0, x1, y1, color):
    draw.ellipse([x0, y0, x1, y1], fill=color)

# ========== 主角: 林凡 (修仙剑客) ==========
# 配色: 黑发、肤色、青蓝色道袍、棕色腰带/靴子、银色剑
PC = {
    "hair":     (25, 20, 30),
    "hair_hl":  (50, 40, 60),
    "skin":     (235, 200, 170),
    "skin_sh":  (210, 170, 140),
    "robe":     (40, 90, 140),
    "robe_lt":  (60, 120, 175),
    "robe_dk":  (25, 60, 100),
    "robe_hl":  (80, 145, 200),
    "belt":     (140, 100, 50),
    "belt_dk":  (110, 75, 35),
    "boot":     (60, 40, 25),
    "boot_dk":  (40, 25, 15),
    "sword_bl": (200, 215, 230),
    "sword_hl": (240, 248, 255),
    "sword_hd": (120, 80, 40),
    "sword_gd": (180, 150, 60),
    "eye":      (30, 25, 20),
    "mouth":    (180, 130, 100),
}

def draw_player_frame(frame_idx, direction):
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    
    # 动画偏移
    bob = int(math.sin(frame_idx * math.pi / 2) * 1.5)
    leg_swing = int(math.sin(frame_idx * math.pi / 2) * 3)
    arm_swing = int(math.sin(frame_idx * math.pi / 2 + math.pi) * 2)
    
    cx = 16  # 中心X
    
    if direction == "down":
        # 正面 - 下半身
        draw_rect(draw, 12, 22+bob, 8, 8+leg_swing, PC["robe_dk"])  # 左腿
        draw_rect(draw, 12+leg_swing, 22+bob, 8, 8-leg_swing, PC["robe_dk"])  # 右腿
        # 靴子
        draw_rect(draw, 11, 28+bob+leg_swing//2, 9, 3, PC["boot"])
        draw_rect(draw, 11+leg_swing//2, 28+bob-leg_swing//2, 9, 3, PC["boot"])
        # 身体 - 道袍
        draw_rect(draw, 10, 14+bob, 12, 10, PC["robe"])
        draw_rect(draw, 11, 14+bob, 2, 10, PC["robe_hl"])  # 左侧高光
        draw_rect(draw, 14, 16+bob, 4, 2, PC["robe_lt"])  # 胸口
        # 腰带
        draw_rect(draw, 10, 22+bob, 12, 2, PC["belt"])
        draw_rect(draw, 14, 22+bob, 2, 2, PC["belt_dk"])  # 带扣
        # 手臂
        draw_rect(draw, 7, 15+bob+arm_swing, 4, 7, PC["robe_dk"])  # 左臂
        draw_rect(draw, 21, 15+bob-arm_swing, 4, 7, PC["robe_dk"])  # 右臂
        # 剑(右手)
        draw_rect(draw, 23, 12+bob-arm_swing, 2, 12, PC["sword_bl"])
        draw_rect(draw, 23, 12+bob-arm_swing, 1, 3, PC["sword_hl"])
        draw_rect(draw, 22, 22+bob-arm_swing, 4, 2, PC["sword_gd"])
        draw_rect(draw, 23, 24+bob-arm_swing, 2, 3, PC["sword_hd"])
        # 头
        draw_ellipse(draw, 11, 5+bob, 20, 14+bob, PC["hair"])
        draw_ellipse(draw, 12, 6+bob, 19, 13+bob, PC["skin"])
        # 头发覆盖
        draw_rect(draw, 11, 4+bob, 10, 5, PC["hair"])
        draw_rect(draw, 10, 5+bob, 2, 4, PC["hair"])
        draw_rect(draw, 20, 5+bob, 2, 4, PC["hair"])
        # 眼睛
        draw_pixel(draw, 14, 10+bob, PC["eye"])
        draw_pixel(draw, 17, 10+bob, PC["eye"])
        # 嘴
        draw_pixel(draw, 15, 12+bob, PC["mouth"])
        draw_pixel(draw, 16, 12+bob, PC["mouth"])
        
    elif direction == "up":
        # 背面
        draw_rect(draw, 12, 22+bob, 8, 8+leg_swing, PC["robe_dk"])
        draw_rect(draw, 12+leg_swing, 22+bob, 8, 8-leg_swing, PC["robe_dk"])
        draw_rect(draw, 11, 28+bob+leg_swing//2, 9, 3, PC["boot"])
        draw_rect(draw, 11+leg_swing//2, 28+bob-leg_swing//2, 9, 3, PC["boot"])
        # 身体
        draw_rect(draw, 10, 14+bob, 12, 10, PC["robe"])
        draw_rect(draw, 14, 14+bob, 2, 10, PC["robe_hl"])
        draw_rect(draw, 10, 22+bob, 12, 2, PC["belt"])
        draw_rect(draw, 14, 22+bob, 2, 2, PC["belt_dk"])
        # 手臂
        draw_rect(draw, 7, 15+bob+arm_swing, 4, 7, PC["robe_dk"])
        draw_rect(draw, 21, 15+bob-arm_swing, 4, 7, PC["robe_dk"])
        # 剑(背后)
        draw_rect(draw, 13, 10+bob, 2, 14, PC["sword_bl"])
        draw_rect(draw, 13, 10+bob, 1, 3, PC["sword_hl"])
        draw_rect(draw, 12, 22+bob, 4, 2, PC["sword_gd"])
        draw_rect(draw, 13, 24+bob, 2, 3, PC["sword_hd"])
        # 头 - 背面头发
        draw_ellipse(draw, 11, 5+bob, 20, 14+bob, PC["hair"])
        draw_rect(draw, 11, 4+bob, 10, 5, PC["hair"])
        # 长发
        draw_rect(draw, 12, 12+bob, 2, 6, PC["hair"])
        draw_rect(draw, 18, 12+bob, 2, 6, PC["hair"])
        
    elif direction == "left":
        # 左侧面
        draw_rect(draw, 13, 22+bob, 6, 8+leg_swing, PC["robe_dk"])  # 后腿
        draw_rect(draw, 13+leg_swing, 22+bob, 6, 8-leg_swing, PC["robe_dk"])  # 前腿
        draw_rect(draw, 12, 28+bob+leg_swing//2, 8, 3, PC["boot"])
        draw_rect(draw, 12+leg_swing//2, 28+bob-leg_swing//2, 8, 3, PC["boot"])
        # 身体
        draw_rect(draw, 11, 14+bob, 10, 10, PC["robe"])
        draw_rect(draw, 12, 14+bob, 3, 10, PC["robe_lt"])
        draw_rect(draw, 11, 22+bob, 10, 2, PC["belt"])
        draw_rect(draw, 12, 22+bob, 2, 2, PC["belt_dk"])
        # 手臂
        draw_rect(draw, 8, 15+bob+arm_swing, 4, 7, PC["robe_dk"])
        # 剑(向前)
        draw_rect(draw, 4, 14+bob+arm_swing, 5, 2, PC["sword_bl"])
        draw_rect(draw, 4, 14+bob+arm_swing, 5, 1, PC["sword_hl"])
        draw_rect(draw, 8, 13+bob+arm_swing, 2, 4, PC["sword_gd"])
        draw_rect(draw, 9, 13+bob+arm_swing, 1, 4, PC["sword_hd"])
        # 头
        draw_ellipse(draw, 12, 5+bob, 21, 14+bob, PC["hair"])
        draw_ellipse(draw, 12, 6+bob, 19, 13+bob, PC["skin"])
        draw_rect(draw, 11, 4+bob, 8, 5, PC["hair"])
        draw_rect(draw, 11, 5+bob, 2, 5, PC["hair"])
        # 眼睛(侧面)
        draw_pixel(draw, 13, 10+bob, PC["eye"])
        # 嘴
        draw_pixel(draw, 13, 12+bob, PC["mouth"])
        
    elif direction == "right":
        # 右侧面
        draw_rect(draw, 13, 22+bob, 6, 8+leg_swing, PC["robe_dk"])
        draw_rect(draw, 13+leg_swing, 22+bob, 6, 8-leg_swing, PC["robe_dk"])
        draw_rect(draw, 12, 28+bob+leg_swing//2, 8, 3, PC["boot"])
        draw_rect(draw, 12+leg_swing//2, 28+bob-leg_swing//2, 8, 3, PC["boot"])
        # 身体
        draw_rect(draw, 11, 14+bob, 10, 10, PC["robe"])
        draw_rect(draw, 15, 14+bob, 3, 10, PC["robe_lt"])
        draw_rect(draw, 11, 22+bob, 10, 2, PC["belt"])
        draw_rect(draw, 16, 22+bob, 2, 2, PC["belt_dk"])
        # 手臂
        draw_rect(draw, 20, 15+bob-arm_swing, 4, 7, PC["robe_dk"])
        # 剑(向前)
        draw_rect(draw, 23, 14+bob-arm_swing, 5, 2, PC["sword_bl"])
        draw_rect(draw, 23, 14+bob-arm_swing, 5, 1, PC["sword_hl"])
        draw_rect(draw, 22, 13+bob-arm_swing, 2, 4, PC["sword_gd"])
        draw_rect(draw, 22, 13+bob-arm_swing, 1, 4, PC["sword_hd"])
        # 头
        draw_ellipse(draw, 11, 5+bob, 20, 14+bob, PC["hair"])
        draw_ellipse(draw, 12, 6+bob, 19, 13+bob, PC["skin"])
        draw_rect(draw, 13, 4+bob, 8, 5, PC["hair"])
        draw_rect(draw, 19, 5+bob, 2, 5, PC["hair"])
        # 眼睛
        draw_pixel(draw, 18, 10+bob, PC["eye"])
        draw_pixel(draw, 18, 12+bob, PC["mouth"])
    
    return img

# ========== 竹妖 (Bamboo Demon) ==========
BC = {
    "bamboo":    (50, 130, 50),
    "bamboo_lt": (80, 170, 80),
    "bamboo_dk": (30, 90, 30),
    "bamboo_hl": (110, 200, 100),
    "leaf":      (40, 160, 60),
    "leaf_lt":   (70, 190, 80),
    "eye":       (220, 220, 50),
    "eye_glow":  (255, 255, 100),
    "mouth":     (180, 40, 40),
    "root":      (100, 70, 40),
    "root_dk":   (70, 50, 25),
    "vine":      (60, 140, 50),
}

def draw_bamboo_frame(frame_idx, direction):
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    
    bob = int(math.sin(frame_idx * math.pi / 2) * 1)
    leg_swing = int(math.sin(frame_idx * math.pi / 2) * 2)
    
    if direction == "down":
        # 根/脚
        draw_rect(draw, 11, 26+bob, 4, 5, BC["root"])
        draw_rect(draw, 17, 26+bob, 4, 5, BC["root"])
        draw_rect(draw, 10, 29+bob, 6, 2, BC["root_dk"])
        draw_rect(draw, 16, 29+bob, 6, 2, BC["root_dk"])
        # 身体 - 竹竿
        draw_rect(draw, 12, 14+bob, 8, 14, BC["bamboo"])
        draw_rect(draw, 13, 14+bob, 2, 14, BC["bamboo_lt"])
        draw_rect(draw, 19, 14+bob, 1, 14, BC["bamboo_dk"])
        # 竹节
        draw_rect(draw, 11, 18+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 11, 24+bob, 10, 2, BC["bamboo_dk"])
        # 竹叶手臂
        draw_rect(draw, 8, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 19, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 6, 15+bob, 3, 2, BC["leaf_lt"])
        draw_rect(draw, 23, 15+bob, 3, 2, BC["leaf_lt"])
        # 头 - 竹节头
        draw_rect(draw, 12, 8+bob, 8, 8, BC["bamboo"])
        draw_rect(draw, 13, 8+bob, 2, 8, BC["bamboo_hl"])
        # 竹叶头发
        draw_rect(draw, 10, 6+bob, 4, 4, BC["leaf"])
        draw_rect(draw, 18, 6+bob, 4, 4, BC["leaf"])
        draw_rect(draw, 12, 5+bob, 8, 3, BC["leaf_lt"])
        # 眼睛
        draw_pixel(draw, 14, 11+bob, BC["eye"])
        draw_pixel(draw, 14, 12+bob, BC["eye_glow"])
        draw_pixel(draw, 17, 11+bob, BC["eye"])
        draw_pixel(draw, 17, 12+bob, BC["eye_glow"])
        # 嘴
        draw_rect(draw, 14, 14+bob, 4, 1, BC["mouth"])
        # 藤蔓
        draw_rect(draw, 7, 20+bob, 2, 5, BC["vine"])
        draw_rect(draw, 23, 20+bob, 2, 5, BC["vine"])
        
    elif direction == "up":
        draw_rect(draw, 11, 26+bob, 4, 5, BC["root"])
        draw_rect(draw, 17, 26+bob, 4, 5, BC["root"])
        draw_rect(draw, 10, 29+bob, 6, 2, BC["root_dk"])
        draw_rect(draw, 16, 29+bob, 6, 2, BC["root_dk"])
        draw_rect(draw, 12, 14+bob, 8, 14, BC["bamboo"])
        draw_rect(draw, 17, 14+bob, 2, 14, BC["bamboo_lt"])
        draw_rect(draw, 11, 18+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 11, 24+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 8, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 19, 16+bob, 5, 2, BC["leaf"])
        # 背面头
        draw_rect(draw, 12, 8+bob, 8, 8, BC["bamboo"])
        draw_rect(draw, 17, 8+bob, 2, 8, BC["bamboo_hl"])
        draw_rect(draw, 12, 5+bob, 8, 3, BC["leaf_lt"])
        draw_rect(draw, 10, 6+bob, 4, 4, BC["leaf"])
        draw_rect(draw, 18, 6+bob, 4, 4, BC["leaf"])
        draw_rect(draw, 7, 20+bob, 2, 5, BC["vine"])
        draw_rect(draw, 23, 20+bob, 2, 5, BC["vine"])
        
    elif direction == "left":
        draw_rect(draw, 12, 26+bob, 5, 5, BC["root"])
        draw_rect(draw, 16, 26+bob, 5, 5, BC["root"])
        draw_rect(draw, 11, 29+bob, 7, 2, BC["root_dk"])
        draw_rect(draw, 15, 29+bob, 7, 2, BC["root_dk"])
        draw_rect(draw, 12, 14+bob, 8, 14, BC["bamboo"])
        draw_rect(draw, 13, 14+bob, 3, 14, BC["bamboo_lt"])
        draw_rect(draw, 11, 18+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 11, 24+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 8, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 19, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 12, 8+bob, 8, 8, BC["bamboo"])
        draw_rect(draw, 13, 8+bob, 3, 8, BC["bamboo_hl"])
        draw_rect(draw, 12, 5+bob, 8, 3, BC["leaf_lt"])
        # 眼睛(侧面)
        draw_pixel(draw, 13, 11+bob, BC["eye"])
        draw_pixel(draw, 13, 12+bob, BC["eye_glow"])
        draw_rect(draw, 13, 14+bob, 3, 1, BC["mouth"])
        draw_rect(draw, 7, 20+bob, 2, 5, BC["vine"])
        
    elif direction == "right":
        draw_rect(draw, 12, 26+bob, 5, 5, BC["root"])
        draw_rect(draw, 16, 26+bob, 5, 5, BC["root"])
        draw_rect(draw, 11, 29+bob, 7, 2, BC["root_dk"])
        draw_rect(draw, 15, 29+bob, 7, 2, BC["root_dk"])
        draw_rect(draw, 12, 14+bob, 8, 14, BC["bamboo"])
        draw_rect(draw, 16, 14+bob, 3, 14, BC["bamboo_lt"])
        draw_rect(draw, 11, 18+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 11, 24+bob, 10, 2, BC["bamboo_dk"])
        draw_rect(draw, 8, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 19, 16+bob, 5, 2, BC["leaf"])
        draw_rect(draw, 12, 8+bob, 8, 8, BC["bamboo"])
        draw_rect(draw, 16, 8+bob, 3, 8, BC["bamboo_hl"])
        draw_rect(draw, 12, 5+bob, 8, 3, BC["leaf_lt"])
        draw_pixel(draw, 18, 11+bob, BC["eye"])
        draw_pixel(draw, 18, 12+bob, BC["eye_glow"])
        draw_rect(draw, 16, 14+bob, 3, 1, BC["mouth"])
        draw_rect(draw, 23, 20+bob, 2, 5, BC["vine"])
    
    return img

# ========== 骷髅将军 (Skeleton General) ==========
SC = {
    "bone":      (220, 215, 200),
    "bone_lt":   (240, 238, 230),
    "bone_dk":   (180, 175, 165),
    "bone_sh":   (150, 145, 135),
    "armor":     (80, 40, 40),
    "armor_lt":  (120, 60, 50),
    "armor_dk":  (55, 25, 25),
    "armor_hl":  (150, 80, 60),
    "gold":      (200, 170, 50),
    "gold_dk":   (160, 130, 30),
    "eye":       (200, 50, 50),
    "eye_glow":  (255, 80, 80),
    "cape":      (60, 20, 20),
    "cape_dk":   (40, 15, 15),
    "weapon":    (160, 155, 150),
    "weapon_hl": (210, 205, 200),
    "weapon_hd": (100, 70, 40),
}

def draw_skeleton_frame(frame_idx, direction):
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    
    bob = int(math.sin(frame_idx * math.pi / 2) * 1)
    leg_swing = int(math.sin(frame_idx * math.pi / 2) * 2)
    
    if direction == "down":
        # 披风(后面)
        draw_rect(draw, 10, 16+bob, 12, 12, SC["cape"])
        draw_rect(draw, 10, 26+bob, 12, 3, SC["cape_dk"])
        # 腿骨
        draw_rect(draw, 12, 24+bob, 3, 6+leg_swing, SC["bone"])
        draw_rect(draw, 17, 24+bob, 3, 6-leg_swing, SC["bone"])
        draw_rect(draw, 12, 23+bob, 3, 2, SC["bone_dk"])  # 膝盖
        draw_rect(draw, 17, 23+bob, 3, 2, SC["bone_dk"])
        # 脚骨
        draw_rect(draw, 11, 28+bob+leg_swing, 4, 2, SC["bone_dk"])
        draw_rect(draw, 16, 28+bob-leg_swing, 4, 2, SC["bone_dk"])
        # 身体 - 铠甲
        draw_rect(draw, 11, 14+bob, 10, 12, SC["armor"])
        draw_rect(draw, 12, 14+bob, 2, 12, SC["armor_hl"])
        draw_rect(draw, 19, 14+bob, 2, 12, SC["armor_dk"])
        # 铠甲装饰
        draw_rect(draw, 11, 18+bob, 10, 2, SC["gold"])
        draw_rect(draw, 11, 22+bob, 10, 2, SC["gold_dk"])
        draw_rect(draw, 15, 14+bob, 2, 4, SC["gold"])  # 胸甲中心
        # 肩甲
        draw_rect(draw, 8, 14+bob, 4, 3, SC["armor"])
        draw_rect(draw, 8, 14+bob, 2, 3, SC["armor_hl"])
        draw_rect(draw, 20, 14+bob, 4, 3, SC["armor"])
        draw_rect(draw, 22, 14+bob, 2, 3, SC["armor_hl"])
        # 手臂骨
        draw_rect(draw, 8, 17+bob, 3, 7, SC["bone"])
        draw_rect(draw, 21, 17+bob, 3, 7, SC["bone"])
        # 手骨
        draw_rect(draw, 8, 23+bob, 3, 2, SC["bone_dk"])
        draw_rect(draw, 21, 23+bob, 3, 2, SC["bone_dk"])
        # 武器 - 大刀(右手)
        draw_rect(draw, 23, 10+bob, 2, 14, SC["weapon"])
        draw_rect(draw, 23, 10+bob, 1, 6, SC["weapon_hl"])
        draw_rect(draw, 22, 22+bob, 4, 2, SC["weapon_hd"])
        draw_rect(draw, 22, 24+bob, 4, 3, SC["weapon_hd"])
        # 头骨
        draw_ellipse(draw, 11, 5+bob, 21, 14+bob, SC["bone"])
        draw_rect(draw, 11, 5+bob, 10, 4, SC["bone"])
        # 眼窝
        draw_rect(draw, 13, 8+bob, 3, 3, (30, 20, 15))
        draw_rect(draw, 17, 8+bob, 3, 3, (30, 20, 15))
        # 眼睛(发光)
        draw_pixel(draw, 14, 9+bob, SC["eye"])
        draw_pixel(draw, 14, 10+bob, SC["eye_glow"])
        draw_pixel(draw, 18, 9+bob, SC["eye"])
        draw_pixel(draw, 18, 10+bob, SC["eye_glow"])
        # 头盔
        draw_rect(draw, 11, 4+bob, 10, 3, SC["armor_dk"])
        draw_rect(draw, 13, 3+bob, 6, 2, SC["armor"])
        draw_rect(draw, 15, 3+bob, 2, 2, SC["gold"])  # 头盔装饰
        # 嘴(骷髅牙)
        draw_rect(draw, 14, 12+bob, 4, 2, SC["bone_dk"])
        draw_rect(draw, 14, 12+bob, 1, 2, SC["bone_lt"])
        draw_rect(draw, 16, 12+bob, 1, 2, SC["bone_lt"])
        draw_rect(draw, 17, 12+bob, 1, 2, SC["bone_lt"])
        
    elif direction == "up":
        # 披风(完全覆盖背面)
        draw_rect(draw, 10, 14+bob, 12, 16, SC["cape"])
        draw_rect(draw, 10, 28+bob, 12, 2, SC["cape_dk"])
        # 腿骨
        draw_rect(draw, 12, 24+bob, 3, 6+leg_swing, SC["bone"])
        draw_rect(draw, 17, 24+bob, 3, 6-leg_swing, SC["bone"])
        draw_rect(draw, 12, 23+bob, 3, 2, SC["bone_dk"])
        draw_rect(draw, 17, 23+bob, 3, 2, SC["bone_dk"])
        draw_rect(draw, 11, 28+bob+leg_swing, 4, 2, SC["bone_dk"])
        draw_rect(draw, 16, 28+bob-leg_swing, 4, 2, SC["bone_dk"])
        # 身体 - 背面铠甲
        draw_rect(draw, 11, 14+bob, 10, 12, SC["armor"])
        draw_rect(draw, 18, 14+bob, 2, 12, SC["armor_hl"])
        draw_rect(draw, 11, 18+bob, 10, 2, SC["gold"])
        draw_rect(draw, 11, 22+bob, 10, 2, SC["gold_dk"])
        draw_rect(draw, 8, 14+bob, 4, 3, SC["armor"])
        draw_rect(draw, 20, 14+bob, 4, 3, SC["armor"])
        # 手臂骨(背面)
        draw_rect(draw, 8, 17+bob, 3, 7, SC["bone"])
        draw_rect(draw, 21, 17+bob, 3, 7, SC["bone"])
        draw_rect(draw, 8, 23+bob, 3, 2, SC["bone_dk"])
        draw_rect(draw, 21, 23+bob, 3, 2, SC["bone_dk"])
        # 武器(右手, 背面)
        draw_rect(draw, 23, 10+bob, 2, 14, SC["weapon"])
        draw_rect(draw, 23, 10+bob, 1, 6, SC["weapon_hl"])
        draw_rect(draw, 22, 22+bob, 4, 2, SC["weapon_hd"])
        draw_rect(draw, 22, 24+bob, 4, 3, SC["weapon_hd"])
        # 头盔背面 - 不画脸和眼睛
        draw_rect(draw, 12, 5+bob, 8, 10, SC["armor_dk"])
        draw_rect(draw, 13, 5+bob, 6, 2, SC["armor"])
        draw_rect(draw, 15, 4+bob, 2, 2, SC["gold"])
        
    elif direction == "left":
        draw_rect(draw, 12, 16+bob, 10, 12, SC["cape"])
        draw_rect(draw, 12, 26+bob, 10, 3, SC["cape_dk"])
        draw_rect(draw, 13, 24+bob, 3, 6+leg_swing, SC["bone"])
        draw_rect(draw, 17, 24+bob, 3, 6-leg_swing, SC["bone"])
        draw_rect(draw, 12, 28+bob+leg_swing, 4, 2, SC["bone_dk"])
        draw_rect(draw, 16, 28+bob-leg_swing, 4, 2, SC["bone_dk"])
        draw_rect(draw, 12, 14+bob, 9, 12, SC["armor"])
        draw_rect(draw, 13, 14+bob, 3, 12, SC["armor_lt"])
        draw_rect(draw, 12, 18+bob, 9, 2, SC["gold"])
        draw_rect(draw, 12, 22+bob, 9, 2, SC["gold_dk"])
        draw_rect(draw, 10, 14+bob, 3, 3, SC["armor"])
        draw_rect(draw, 10, 17+bob, 3, 7, SC["bone"])
        # 头骨侧面
        draw_ellipse(draw, 12, 5+bob, 21, 14+bob, SC["bone"])
        draw_rect(draw, 12, 5+bob, 9, 4, SC["bone"])
        draw_rect(draw, 12, 4+bob, 9, 3, SC["armor_dk"])
        # 眼窝
        draw_rect(draw, 13, 8+bob, 3, 3, (30, 20, 15))
        draw_pixel(draw, 14, 9+bob, SC["eye"])
        draw_pixel(draw, 14, 10+bob, SC["eye_glow"])
        draw_rect(draw, 13, 12+bob, 3, 2, SC["bone_dk"])
        # 武器(向前)
        draw_rect(draw, 6, 12+bob, 5, 2, SC["weapon"])
        draw_rect(draw, 6, 12+bob, 5, 1, SC["weapon_hl"])
        draw_rect(draw, 6, 11+bob, 2, 4, SC["weapon_hd"])
        
    elif direction == "right":
        draw_rect(draw, 10, 16+bob, 10, 12, SC["cape"])
        draw_rect(draw, 10, 26+bob, 10, 3, SC["cape_dk"])
        draw_rect(draw, 13, 24+bob, 3, 6+leg_swing, SC["bone"])
        draw_rect(draw, 17, 24+bob, 3, 6-leg_swing, SC["bone"])
        draw_rect(draw, 12, 28+bob+leg_swing, 4, 2, SC["bone_dk"])
        draw_rect(draw, 16, 28+bob-leg_swing, 4, 2, SC["bone_dk"])
        draw_rect(draw, 11, 14+bob, 9, 12, SC["armor"])
        draw_rect(draw, 16, 14+bob, 3, 12, SC["armor_lt"])
        draw_rect(draw, 11, 18+bob, 9, 2, SC["gold"])
        draw_rect(draw, 11, 22+bob, 9, 2, SC["gold_dk"])
        draw_rect(draw, 19, 14+bob, 3, 3, SC["armor"])
        draw_rect(draw, 19, 17+bob, 3, 7, SC["bone"])
        draw_ellipse(draw, 11, 5+bob, 20, 14+bob, SC["bone"])
        draw_rect(draw, 11, 5+bob, 9, 4, SC["bone"])
        draw_rect(draw, 11, 4+bob, 9, 3, SC["armor_dk"])
        draw_rect(draw, 16, 8+bob, 3, 3, (30, 20, 15))
        draw_pixel(draw, 17, 9+bob, SC["eye"])
        draw_pixel(draw, 17, 10+bob, SC["eye_glow"])
        draw_rect(draw, 16, 12+bob, 3, 2, SC["bone_dk"])
        draw_rect(draw, 22, 12+bob, 5, 2, SC["weapon"])
        draw_rect(draw, 22, 12+bob, 5, 1, SC["weapon_hl"])
        draw_rect(draw, 24, 11+bob, 2, 4, SC["weapon_hd"])
    
    return img

# ========== 生成精灵表 ==========
def make_spritesheet(draw_fn, filename):
    sheet = Image.new("RGBA", (FRAME_SIZE * GRID, FRAME_SIZE * GRID), (0, 0, 0, 0))
    for row, dir_name in enumerate(DIR_NAMES):
        for col in range(GRID):
            frame = draw_fn(col, dir_name)
            sheet.paste(frame, (col * FRAME_SIZE, row * FRAME_SIZE), frame)
    path = os.path.join(SPRITE_DIR, filename)
    sheet.save(path, "PNG")
    print(f"Saved {path} ({FRAME_SIZE*GRID}x{FRAME_SIZE*GRID})")

def main():
    os.makedirs(SPRITE_DIR, exist_ok=True)
    make_spritesheet(draw_player_frame, "player.png")
    make_spritesheet(draw_bamboo_frame, "enemy_bamboo.png")
    make_spritesheet(draw_skeleton_frame, "enemy_skeleton.png")
    print("Done!")

if __name__ == "__main__":
    main()
