#!/usr/bin/env python3
"""生成中国风地图 - 用tileset中的34种tiles构建场景."""
import json
import os
import math

MAPS_DIR = os.path.join(os.path.dirname(__file__), 'maps')
os.makedirs(MAPS_DIR, exist_ok=True)

# Tile IDs (1-indexed)
T = {
    "GRASS": 1, "DIRT": 2, "STONE_PATH": 3, "STONE_PATH_H": 4, "STONE_PATH_V": 5,
    "WATER": 6, "WATER_EDGE_T": 7, "WATER_EDGE_B": 8,
    "BAMBOO": 9, "BAMBOO_THICK": 10, "POND": 11, "ROCK": 12, "FLOWER": 13,
    "WALL": 14, "WALL_CORNER": 15, "WOOD_FLOOR": 16, "DOOR": 17,
    "PILLAR": 18, "ROOF": 19, "LANTERN": 20, "STONE_LION": 21,
    "BRIDGE": 22, "STEPS": 23, "WELL": 24, "CHEST": 25, "STONE_TABLE": 26,
    "FENCE": 27, "GATE": 28, "MOON_GATE": 29, "ALTAR": 30,
    "TORCH": 31, "VOID": 32, "MOUNTAIN": 33, "GARDEN_ROCK": 34,
}

W, H = 24, 18  # 地图尺寸

def make_empty_map(w=W, h=H, fill=T["GRASS"]):
    return [[fill] * w for _ in range(h)]

def fill_rect(tiles, x1, y1, x2, y2, tile):
    for y in range(y1, min(y2+1, len(tiles))):
        for x in range(x1, min(x2+1, len(tiles[0]))):
            tiles[y][x] = tile

def draw_path_h(tiles, y, x1, x2, tile=T["STONE_PATH"]):
    for x in range(x1, x2+1):
        if 0 <= x < len(tiles[0]) and 0 <= y < len(tiles):
            tiles[y][x] = tile

def draw_path_v(tiles, x, y1, y2, tile=T["STONE_PATH"]):
    for y in range(y1, y2+1):
        if 0 <= x < len(tiles[0]) and 0 <= y < len(tiles):
            tiles[y][x] = tile

def draw_rect_border(tiles, x1, y1, x2, y2, border, fill_inside=None):
    """画矩形框."""
    for x in range(x1, x2+1):
        tiles[y1][x] = border
        tiles[y2][x] = border
    for y in range(y1, y2+1):
        tiles[y][x1] = border
        tiles[y][x2] = border
    if fill_inside:
        for y in range(y1+1, y2):
            for x in range(x1+1, x2):
                tiles[y][x] = fill_inside

# ====== 青石镇广场 ======
def gen_qingshi_town():
    tiles = make_empty_map(24, 18)
    
    # 广场地面 - 青石板
    fill_rect(tiles, 4, 4, 19, 13, T["STONE_PATH"])
    
    # 广场边缘草地
    for y in range(4, 14):
        tiles[y][4] = T["GRASS"]
        tiles[y][19] = T["GRASS"]
    
    # 主路 - 南北向石板路
    draw_path_v(tiles, 11, 0, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 0, 17, T["STONE_PATH_V"])
    
    # 横路 - 东西向
    draw_path_h(tiles, 8, 0, 23, T["STONE_PATH_H"])
    draw_path_h(tiles, 9, 0, 23, T["STONE_PATH_H"])
    
    # 建筑 - 南面大厅
    draw_rect_border(tiles, 2, 14, 8, 17, T["WALL"], T["WOOD_FLOOR"])
    tiles[17][5] = T["DOOR"]  # 门
    
    # 建筑 - 东面商店
    draw_rect_border(tiles, 20, 14, 23, 17, T["WALL"], T["WOOD_FLOOR"])
    tiles[17][20] = T["DOOR"]
    
    # 建筑 - 西面药铺
    draw_rect_border(tiles, 0, 0, 3, 3, T["WALL"], T["WOOD_FLOOR"])
    tiles[3][1] = T["DOOR"]
    
    # 柱子装饰
    tiles[14][3] = T["PILLAR"]
    tiles[14][7] = T["PILLAR"]
    
    # 灯笼
    tiles[14][2] = T["LANTERN"]
    tiles[14][8] = T["LANTERN"]
    
    # 石狮子
    tiles[13][3] = T["STONE_LION"]
    tiles[13][7] = T["STONE_LION"]
    
    # 牌坊/门楼 - 镇口
    tiles[17][10] = T["GATE"]
    tiles[17][11] = T["GATE"]
    tiles[17][12] = T["GATE"]
    tiles[17][13] = T["GATE"]
    
    # 池塘 - 广场东北角
    tiles[5][17] = T["POND"]
    tiles[5][18] = T["POND"]
    tiles[6][17] = T["POND"]
    tiles[6][18] = T["POND"]
    
    # 花坛
    tiles[5][2] = T["FLOWER"]
    tiles[5][3] = T["FLOWER"]
    tiles[6][2] = T["FLOWER"]
    
    # 竹林 - 西北角
    for y in range(0, 4):
        for x in range(4, 8):
            tiles[y][x] = T["BAMBOO"]
    tiles[0][4] = T["BAMBOO_THICK"]
    tiles[0][5] = T["BAMBOO_THICK"]
    tiles[1][4] = T["BAMBOO_THICK"]
    
    # 石桌 - 休息区
    tiles[6][6] = T["STONE_TABLE"]
    tiles[6][7] = T["STONE_TABLE"]
    
    # 古井
    tiles[7][4] = T["WELL"]
    
    # 太湖石装饰
    tiles[6][15] = T["GARDEN_ROCK"]
    tiles[7][16] = T["ROCK"]
    
    # 竹篱笆 - 围住竹林
    for x in range(4, 8):
        tiles[4][x] = T["FENCE"]
    for y in range(0, 5):
        tiles[y][3] = T["FENCE"] if tiles[y][3] != T["BAMBOO"] else T["BAMBOO"]
        tiles[y][8] = T["FENCE"] if tiles[y][8] != T["BAMBOO"] else T["BAMBOO"]
    
    # 月亮门 - 通往下一个场景
    tiles[8][20] = T["MOON_GATE"]
    tiles[9][20] = T["MOON_GATE"]
    
    # 台阶
    draw_path_h(tiles, 13, 4, 8, T["STEPS"])
    
    return tiles

# ====== 门派清晨 (sect_morning) ======
def gen_sect_morning():
    tiles = make_empty_map(24, 18)
    
    # 主殿
    draw_rect_border(tiles, 8, 2, 15, 6, T["WALL"], T["WOOD_FLOOR"])
    tiles[6][11] = T["DOOR"]
    tiles[6][12] = T["DOOR"]
    
    # 屋顶效果 - 殿顶用特殊tile
    for x in range(8, 16):
        tiles[2][x] = T["ROOF"]
    
    # 柱子
    tiles[6][9] = T["PILLAR"]
    tiles[6][14] = T["PILLAR"]
    tiles[3][9] = T["PILLAR"]
    tiles[3][14] = T["PILLAR"]
    
    # 石阶通向主殿
    for y in range(7, 12):
        tiles[y][10] = T["STEPS"]
        tiles[y][11] = T["STEPS"]
        tiles[y][12] = T["STEPS"]
        tiles[y][13] = T["STEPS"]
    
    # 石板路
    draw_path_v(tiles, 10, 12, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 11, 12, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 12, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 13, 12, 17, T["STONE_PATH_V"])
    
    # 东厢房
    draw_rect_border(tiles, 17, 4, 22, 8, T["WALL"], T["WOOD_FLOOR"])
    tiles[8][18] = T["DOOR"]
    tiles[5][17] = T["PILLAR"]
    tiles[5][22] = T["PILLAR"]
    
    # 西厢房
    draw_rect_border(tiles, 1, 4, 6, 8, T["WALL"], T["WOOD_FLOOR"])
    tiles[8][2] = T["DOOR"]
    tiles[5][2] = T["PILLAR"]
    tiles[5][5] = T["PILLAR"]
    
    # 庭院石板
    fill_rect(tiles, 8, 8, 15, 12, T["STONE_PATH"])
    # 草地围绕
    for y in range(8, 13):
        tiles[y][8] = T["GRASS"]
        tiles[y][15] = T["GRASS"]
    
    # 花坛
    tiles[9][9] = T["FLOWER"]
    tiles[9][14] = T["FLOWER"]
    tiles[11][9] = T["FLOWER"]
    tiles[11][14] = T["FLOWER"]
    
    # 石桌
    tiles[10][11] = T["STONE_TABLE"]
    tiles[10][12] = T["STONE_TABLE"]
    
    # 灯笼
    tiles[3][8] = T["LANTERN"]
    tiles[3][15] = T["LANTERN"]
    
    # 石狮子
    tiles[7][9] = T["STONE_LION"]
    tiles[7][14] = T["STONE_LION"]
    
    # 竹林
    for y in range(0, 3):
        for x in range(0, 4):
            tiles[y][x] = T["BAMBOO"]
    tiles[0][0] = T["BAMBOO_THICK"]
    tiles[0][1] = T["BAMBOO_THICK"]
    tiles[1][0] = T["BAMBOO_THICK"]
    
    for y in range(0, 3):
        for x in range(20, 24):
            tiles[y][x] = T["BAMBOO"]
    tiles[0][22] = T["BAMBOO_THICK"]
    tiles[1][23] = T["BAMBOO_THICK"]
    
    # 牌坊 - 山门
    tiles[17][8] = T["GATE"]
    tiles[17][9] = T["GATE"]
    tiles[17][14] = T["GATE"]
    tiles[17][15] = T["GATE"]
    
    # 月亮门 - 通向后山
    tiles[12][22] = T["MOON_GATE"]
    tiles[13][22] = T["MOON_GATE"]
    
    # 围墙
    for x in range(0, 24):
        if x < 8 or x > 15:
            tiles[0][x] = T["WALL"] if tiles[0][x] != T["BAMBOO"] else tiles[0][x]
    
    return tiles

# ====== Boss战场景 (boss_battle) ======
def gen_boss_battle():
    tiles = make_empty_map(24, 18)
    
    # 战斗场地 - 深色石板
    fill_rect(tiles, 4, 4, 19, 13, T["STONE_PATH"])
    
    # 边缘草地
    for y in range(3, 15):
        tiles[y][4] = T["GRASS"]
        tiles[y][19] = T["GRASS"]
    
    # 祭坛/炼丹炉 - 场地中央
    tiles[8][11] = T["ALTAR"]
    tiles[8][12] = T["ALTAR"]
    
    # 火把 - 四周
    tiles[4][5] = T["TORCH"]
    tiles[4][18] = T["TORCH"]
    tiles[13][5] = T["TORCH"]
    tiles[13][18] = T["TORCH"]
    
    # 石柱
    tiles[5][6] = T["PILLAR"]
    tiles[5][17] = T["PILLAR"]
    tiles[12][6] = T["PILLAR"]
    tiles[12][17] = T["PILLAR"]
    
    # 石桌/宝箱
    tiles[6][10] = T["CHEST"]
    tiles[6][13] = T["CHEST"]
    
    # 太湖石装饰
    tiles[6][6] = T["GARDEN_ROCK"]
    tiles[6][17] = T["GARDEN_ROCK"]
    tiles[11][6] = T["GARDEN_ROCK"]
    tiles[11][17] = T["GARDEN_ROCK"]
    
    # 竹林边缘
    for y in range(0, 4):
        for x in range(0, 5):
            tiles[y][x] = T["BAMBOO_THICK"]
    for y in range(0, 4):
        for x in range(19, 24):
            tiles[y][x] = T["BAMBOO_THICK"]
    for y in range(14, 18):
        for x in range(0, 24):
            tiles[y][x] = T["BAMBOO_THICK"]
    
    # 入口
    tiles[17][11] = T["MOON_GATE"]
    tiles[17][12] = T["MOON_GATE"]
    
    return tiles

# ====== 古墓大厅 (tomb_hall) ======
def gen_tomb_hall():
    tiles = make_empty_map(24, 18)
    
    # 暗色调地面
    fill_rect(tiles, 0, 0, 23, 17, T["DIRT"])
    
    # 中央石板路
    draw_path_v(tiles, 11, 0, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 0, 17, T["STONE_PATH_V"])
    
    # 墙壁
    for x in range(0, 24):
        tiles[0][x] = T["WALL"]
        tiles[17][x] = T["WALL"]
    for y in range(0, 18):
        tiles[y][0] = T["WALL"]
        tiles[y][23] = T["WALL"]
    
    # 柱子
    tiles[2][4] = T["PILLAR"]
    tiles[2][19] = T["PILLAR"]
    tiles[15][4] = T["PILLAR"]
    tiles[15][19] = T["PILLAR"]
    
    # 火把
    tiles[2][3] = T["TORCH"]
    tiles[2][20] = T["TORCH"]
    tiles[15][3] = T["TORCH"]
    tiles[15][20] = T["TORCH"]
    
    # 祭坛
    tiles[2][11] = T["ALTAR"]
    tiles[2][12] = T["ALTAR"]
    
    # 宝箱
    tiles[8][8] = T["CHEST"]
    tiles[8][15] = T["CHEST"]
    tiles[12][8] = T["CHEST"]
    tiles[12][15] = T["CHEST"]
    
    # 石门
    tiles[8][10] = T["GATE"]
    tiles[8][11] = T["GATE"]
    tiles[8][12] = T["GATE"]
    tiles[8][13] = T["GATE"]
    
    return tiles

# ====== 古墓入口 (tomb_entry) ======
def gen_tomb_entry():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["GRASS"])
    
    # 小路
    draw_path_v(tiles, 11, 17, 5, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 17, 5, T["STONE_PATH_V"])
    
    # 入口
    tiles[5][10] = T["GATE"]
    tiles[5][11] = T["GATE"]
    tiles[5][12] = T["GATE"]
    tiles[5][13] = T["GATE"]
    
    # 石狮子
    tiles[6][9] = T["STONE_LION"]
    tiles[6][14] = T["STONE_LION"]
    
    # 竹林
    for x in range(0, 6):
        tiles[10][x] = T["BAMBOO"]
        tiles[11][x] = T["BAMBOO"]
        tiles[12][x] = T["BAMBOO"]
        tiles[13][x] = T["BAMBOO"]
    for x in range(18, 24):
        tiles[10][x] = T["BAMBOO"]
        tiles[11][x] = T["BAMBOO"]
        tiles[12][x] = T["BAMBOO"]
        tiles[13][x] = T["BAMBOO"]
    
    # 山石
    tiles[8][3] = T["ROCK"]
    tiles[8][20] = T["ROCK"]
    tiles[10][2] = T["GARDEN_ROCK"]
    tiles[10][21] = T["GARDEN_ROCK"]
    
    # 火把
    tiles[6][10] = T["TORCH"]
    tiles[6][13] = T["TORCH"]
    
    return tiles

# ====== 竹林迷雾 (bamboo_fog) ======
def gen_bamboo_fog():
    tiles = make_empty_map(24, 18)
    
    # 大部分是竹林
    for y in range(0, 18):
        for x in range(0, 24):
            if (x + y) % 3 == 0:
                tiles[y][x] = T["BAMBOO_THICK"]
            else:
                tiles[y][x] = T["BAMBOO"]
    
    # 小路穿过竹林
    draw_path_v(tiles, 11, 17, 0, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 17, 0, T["STONE_PATH_V"])
    
    # 横向小路
    draw_path_h(tiles, 8, 3, 20, T["STONE_PATH_H"])
    draw_path_h(tiles, 9, 3, 20, T["STONE_PATH_H"])
    
    # 石桌
    tiles[8][5] = T["STONE_TABLE"]
    tiles[9][18] = T["STONE_TABLE"]
    
    # 古井
    tiles[6][8] = T["WELL"]
    
    # 竹林中的石灯
    tiles[4][6] = T["LANTERN"]
    tiles[4][17] = T["LANTERN"]
    tiles[14][6] = T["LANTERN"]
    tiles[14][17] = T["LANTERN"]
    
    # 花坛
    tiles[10][4] = T["FLOWER"]
    tiles[10][19] = T["FLOWER"]
    
    return tiles

# ====== 竹林深处 (bamboo_deep) ======
def gen_bamboo_deep():
    tiles = make_empty_map(24, 18)
    
    # 更密集的竹林
    for y in range(0, 18):
        for x in range(0, 24):
            tiles[y][x] = T["BAMBOO_THICK"]
    
    # Boss空地
    fill_rect(tiles, 8, 6, 15, 12, T["STONE_PATH"])
    
    # 空地边缘灯笼
    tiles[6][8] = T["LANTERN"]
    tiles[6][15] = T["LANTERN"]
    tiles[12][8] = T["LANTERN"]
    tiles[12][15] = T["LANTERN"]
    
    # 祭坛
    tiles[9][11] = T["ALTAR"]
    tiles[9][12] = T["ALTAR"]
    
    # 小路通向空地
    draw_path_v(tiles, 11, 17, 13, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 17, 13, T["STONE_PATH_V"])
    
    return tiles

# ====== 雪地/冰谷 ======
def gen_snow_field():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["GRASS"])
    
    # 冰面
    fill_rect(tiles, 4, 6, 19, 12, T["WATER"])
    
    # 石桥跨越冰面
    tiles[8][4] = T["BRIDGE"]
    tiles[8][5] = T["BRIDGE"]
    tiles[9][4] = T["BRIDGE"]
    tiles[9][5] = T["BRIDGE"]
    tiles[8][18] = T["BRIDGE"]
    tiles[8][19] = T["BRIDGE"]
    tiles[9][18] = T["BRIDGE"]
    tiles[9][19] = T["BRIDGE"]
    
    # 小路
    draw_path_h(tiles, 8, 0, 3, T["STONE_PATH_H"])
    draw_path_h(tiles, 9, 0, 3, T["STONE_PATH_H"])
    draw_path_h(tiles, 8, 6, 17, T["STONE_PATH_H"])
    draw_path_h(tiles, 9, 6, 17, T["STONE_PATH_H"])
    draw_path_h(tiles, 8, 20, 23, T["STONE_PATH_H"])
    draw_path_h(tiles, 9, 20, 23, T["STONE_PATH_H"])
    
    # 山石
    tiles[4][3] = T["ROCK"]
    tiles[4][20] = T["ROCK"]
    tiles[14][3] = T["GARDEN_ROCK"]
    tiles[14][20] = T["GARDEN_ROCK"]
    
    # 竹林(稀疏)
    tiles[2][0] = T["BAMBOO"]
    tiles[2][1] = T["BAMBOO"]
    tiles[3][0] = T["BAMBOO"]
    tiles[2][22] = T["BAMBOO"]
    tiles[2][23] = T["BAMBOO"]
    
    return tiles

# ====== 冰谷 (ice_valley) ======
def gen_ice_valley():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["GRASS"])
    
    # 更多冰面
    fill_rect(tiles, 2, 4, 21, 14, T["WATER"])
    
    # 曲折小路
    draw_path_v(tiles, 5, 0, 3, T["STONE_PATH_V"])
    draw_path_v(tiles, 6, 0, 3, T["STONE_PATH_V"])
    draw_path_h(tiles, 3, 6, 12, T["STONE_PATH_H"])
    draw_path_v(tiles, 12, 3, 8, T["STONE_PATH_V"])
    draw_path_v(tiles, 13, 3, 8, T["STONE_PATH_V"])
    draw_path_h(tiles, 8, 12, 18, T["STONE_PATH_H"])
    draw_path_v(tiles, 18, 8, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 19, 8, 17, T["STONE_PATH_V"])
    
    # 山石
    tiles[5][8] = T["ROCK"]
    tiles[5][14] = T["ROCK"]
    tiles[10][8] = T["GARDEN_ROCK"]
    tiles[10][14] = T["GARDEN_ROCK"]
    
    # Boss空地
    fill_rect(tiles, 14, 12, 17, 14, T["STONE_PATH"])
    tiles[13][14] = T["ALTAR"]
    
    return tiles

# ====== 龙巢 (dragon_den) ======
def gen_dragon_den():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["DIRT"])
    
    # 龙巢空地
    fill_rect(tiles, 6, 4, 17, 14, T["STONE_PATH"])
    
    # 石柱环绕
    for x in [6, 17]:
        for y in [4, 14]:
            tiles[y][x] = T["PILLAR"]
    
    # 祭坛
    tiles[9][11] = T["ALTAR"]
    tiles[9][12] = T["ALTAR"]
    
    # 火把
    tiles[4][7] = T["TORCH"]
    tiles[4][16] = T["TORCH"]
    tiles[14][7] = T["TORCH"]
    tiles[14][16] = T["TORCH"]
    
    # 宝箱
    tiles[6][8] = T["CHEST"]
    tiles[6][15] = T["CHEST"]
    
    # 太湖石
    tiles[5][9] = T["GARDEN_ROCK"]
    tiles[5][14] = T["GARDEN_ROCK"]
    
    return tiles

# ====== 山峰 (peak_theme / luoxia_peak) ======
def gen_peak():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["GRASS"])
    
    # 山顶平台
    fill_rect(tiles, 6, 6, 17, 12, T["STONE_PATH"])
    
    # 石阶上山
    draw_path_v(tiles, 11, 12, 17, T["STEPS"])
    draw_path_v(tiles, 12, 12, 17, T["STEPS"])
    
    # 栏杆
    for y in range(6, 13):
        tiles[y][6] = T["FENCE"]
        tiles[y][17] = T["FENCE"]
    
    # 祭坛/炼丹炉
    tiles[9][11] = T["ALTAR"]
    tiles[9][12] = T["ALTAR"]
    
    # 石桌
    tiles[8][8] = T["STONE_TABLE"]
    tiles[8][15] = T["STONE_TABLE"]
    
    # 灯笼
    tiles[7][7] = T["LANTERN"]
    tiles[7][16] = T["LANTERN"]
    tiles[11][7] = T["LANTERN"]
    tiles[11][16] = T["LANTERN"]
    
    # 山石
    tiles[5][4] = T["MOUNTAIN"]
    tiles[5][19] = T["MOUNTAIN"]
    tiles[4][11] = T["ROCK"]
    
    return tiles

# ====== 大厅 (hall_music / taiqing_hall) ======
def gen_hall():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["WOOD_FLOOR"])
    
    # 墙壁
    for x in range(0, 24):
        tiles[0][x] = T["WALL"]
        tiles[17][x] = T["WALL"]
    for y in range(0, 18):
        tiles[y][0] = T["WALL"]
        tiles[y][23] = T["WALL"]
    
    # 柱子
    for y in [2, 8, 14]:
        tiles[y][4] = T["PILLAR"]
        tiles[y][19] = T["PILLAR"]
    
    # 门
    tiles[17][11] = T["DOOR"]
    tiles[17][12] = T["DOOR"]
    
    # 灯笼
    tiles[2][6] = T["LANTERN"]
    tiles[2][17] = T["LANTERN"]
    tiles[8][6] = T["LANTERN"]
    tiles[8][17] = T["LANTERN"]
    
    # 石桌
    tiles[8][11] = T["STONE_TABLE"]
    tiles[8][12] = T["STONE_TABLE"]
    
    # 宝箱
    tiles[14][8] = T["CHEST"]
    tiles[14][15] = T["CHEST"]
    
    return tiles

# ====== 安静房间 ======
def gen_quiet_room():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["WOOD_FLOOR"])
    
    for x in range(0, 24):
        tiles[0][x] = T["WALL"]
        tiles[17][x] = T["WALL"]
    for y in range(0, 18):
        tiles[y][0] = T["WALL"]
        tiles[y][23] = T["WALL"]
    
    tiles[17][11] = T["DOOR"]
    
    # 床铺区域(用木地板表示)
    fill_rect(tiles, 15, 15, 20, 16, T["WOOD_FLOOR"])
    
    # 石桌
    tiles[8][11] = T["STONE_TABLE"]
    tiles[8][12] = T["STONE_TABLE"]
    
    return tiles

# ====== 门派入口 (sect_entrance / qingyun_gate) ======
def gen_sect_entrance():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["GRASS"])
    
    # 牌坊 - 山门
    for x in range(8, 16):
        tiles[10][x] = T["GATE"]
    
    # 石阶上山
    draw_path_v(tiles, 11, 11, 17, T["STEPS"])
    draw_path_v(tiles, 12, 11, 17, T["STEPS"])
    
    # 石板路
    draw_path_h(tiles, 10, 4, 7, T["STONE_PATH_H"])
    draw_path_h(tiles, 10, 16, 19, T["STONE_PATH_H"])
    
    # 石狮子
    tiles[11][7] = T["STONE_LION"]
    tiles[11][16] = T["STONE_LION"]
    
    # 灯笼
    tiles[10][5] = T["LANTERN"]
    tiles[10][18] = T["LANTERN"]
    
    # 竹林
    for y in range(6, 11):
        for x in range(0, 4):
            tiles[y][x] = T["BAMBOO"]
    for y in range(6, 11):
        for x in range(20, 24):
            tiles[y][x] = T["BAMBOO"]
    
    # 山石
    tiles[8][3] = T["MOUNTAIN"]
    tiles[8][20] = T["MOUNTAIN"]
    
    return tiles

# ====== 魔谷 (demon_valley) ======
def gen_demon_valley():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["DIRT"])
    
    # 中央空地
    fill_rect(tiles, 6, 5, 17, 13, T["STONE_PATH"])
    
    # 竹林边缘(暗色)
    for y in range(0, 18):
        for x in range(0, 6):
            tiles[y][x] = T["BAMBOO_THICK"]
        for x in range(18, 24):
            tiles[y][x] = T["BAMBOO_THICK"]
    
    # 火把
    tiles[5][7] = T["TORCH"]
    tiles[5][16] = T["TORCH"]
    tiles[13][7] = T["TORCH"]
    tiles[13][16] = T["TORCH"]
    
    # 祭坛
    tiles[9][11] = T["ALTAR"]
    tiles[9][12] = T["ALTAR"]
    
    # 宝箱
    tiles[7][9] = T["CHEST"]
    tiles[7][14] = T["CHEST"]
    
    return tiles

# ====== 魔谷深处 ======
def gen_demon_mid():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["DIRT"])
    
    # 更密集竹林
    for y in range(0, 18):
        for x in range(0, 24):
            tiles[y][x] = T["BAMBOO_THICK"]
    
    # Boss空地
    fill_rect(tiles, 8, 6, 15, 12, T["STONE_PATH"])
    
    # 祭坛
    tiles[9][11] = T["ALTAR"]
    tiles[9][12] = T["ALTAR"]
    
    # 火把
    tiles[6][9] = T["TORCH"]
    tiles[6][14] = T["TORCH"]
    tiles[12][9] = T["TORCH"]
    tiles[12][14] = T["TORCH"]
    
    # 小路
    draw_path_v(tiles, 11, 13, 17, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 13, 17, T["STONE_PATH_V"])
    
    return tiles

# ====== 古墓深处 ======
def gen_tomb_deep():
    tiles = make_empty_map(24, 18)
    
    fill_rect(tiles, 0, 0, 23, 17, T["DIRT"])
    
    # 墙壁
    for x in range(0, 24):
        tiles[0][x] = T["WALL"]
        tiles[17][x] = T["WALL"]
    for y in range(0, 18):
        tiles[y][0] = T["WALL"]
        tiles[y][23] = T["WALL"]
    
    # 石板路
    draw_path_v(tiles, 11, 1, 16, T["STONE_PATH_V"])
    draw_path_v(tiles, 12, 1, 16, T["STONE_PATH_V"])
    
    # 柱子
    tiles[3][5] = T["PILLAR"]
    tiles[3][18] = T["PILLAR"]
    tiles[14][5] = T["PILLAR"]
    tiles[14][18] = T["PILLAR"]
    
    # 火把
    tiles[3][4] = T["TORCH"]
    tiles[3][19] = T["TORCH"]
    tiles[14][4] = T["TORCH"]
    tiles[14][19] = T["TORCH"]
    
    # Boss祭坛
    tiles[3][11] = T["ALTAR"]
    tiles[3][12] = T["ALTAR"]
    
    # 宝箱
    tiles[8][8] = T["CHEST"]
    tiles[8][15] = T["CHEST"]
    tiles[12][8] = T["CHEST"]
    tiles[12][15] = T["CHEST"]
    
    return tiles

# ====== Generate all maps ======
map_funcs = {
    "ch01_qingshi_town": (gen_qingshi_town, "青石镇广场", "town_theme.ogg"),
    "sect_main": (gen_sect_morning, "门派大殿", "sect_morning.ogg"),
    "ch02_bamboo_boss": (gen_boss_battle, "Boss战场", "boss_battle.ogg"),
    "ch03_tomb_hall": (gen_tomb_hall, "古墓大厅", "tomb_hall.ogg"),
    "ch03_tomb_entry": (gen_tomb_entry, "古墓入口", "tomb_entrance.ogg"),
    "ch02_bamboo_entry": (gen_bamboo_fog, "竹林迷雾", "bamboo_fog.ogg"),
    "ch02_bamboo_deep": (gen_bamboo_deep, "竹林深处", "bamboo_deep.ogg"),
    "ch05_north_entry": (gen_snow_field, "雪地", "snow_field.ogg"),
    "ch05_ice_valley": (gen_ice_valley, "冰谷", "ice_valley.ogg"),
    "ch05_dragon_den": (gen_dragon_den, "龙巢", "dragon_den.ogg"),
    "ch05_peak": (gen_peak, "落霞峰", "peak_theme.ogg"),
    "ch01_taiqing_hall": (gen_hall, "太清殿", "hall_music.ogg"),
    "ch01_luoxia_room": (gen_quiet_room, "静室", "quiet_room.ogg"),
    "ch01_qingyun_gate": (gen_sect_entrance, "青云门", "sect_entrance.ogg"),
    "ch04_demon_entry": (gen_demon_valley, "魔谷入口", "demon_valley.ogg"),
    "ch04_demon_mid": (gen_demon_mid, "魔谷深处", "demon_mid.ogg"),
    "ch03_tomb_deep": (gen_tomb_deep, "古墓深处", "tomb_deep.ogg"),
    "ch03_tomb_boss": (gen_tomb_deep, "古墓Boss", "boss_battle.ogg"),  # same as deep
    "ch04_demon_boss": (gen_demon_mid, "魔谷Boss", "boss_battle.ogg"),
    "ch05_heaven_platform": (gen_peak, "天台", "boss_battle.ogg"),
}

def save_map(filename, tiles, name, music):
    path = os.path.join(MAPS_DIR, filename)
    data = {
        "id": filename.replace('.json', ''),
        "name": name,
        "music": music,
        "tiles": tiles,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {path}")

def main():
    for filename, (gen_func, name, music) in map_funcs.items():
        tiles = gen_func()
        save_map(filename + '.json', tiles, name, music)
    print(f"\nGenerated {len(map_funcs)} maps!")

if __name__ == "__main__":
    main()
