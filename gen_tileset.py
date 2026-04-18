#!/usr/bin/env python3
"""Generate pixel art tileset for Xianxia RPG."""
from PIL import Image, ImageDraw
import os

TILES_DIR = "/root/xianxia-rpg/assets/tiles"
T = 32
sheet_w = 32 * 10
sheet_h = 32 * 8
tileset = Image.new('RGBA', (sheet_w, sheet_h), (0, 0, 0, 0))

def make_tile(draw_func):
    img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_func(d)
    return img

# === Row 0: Ground basics ===
def grass():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        for x in range(8):
            for y in range(8):
                if (x+y)%3==0:
                    d.rectangle([x*4, y*4, x*4+2, y*4+2], fill=(60,140,40))
    return f

def dirt():
    def f(d):
        d.rectangle([0,0,32,32], fill=(160,140,100))
        for x in range(6):
            for y in range(6):
                d.rectangle([x*5, y*5, x*5+3, y*5+3], fill=(140,120,80))
    return f

def stone_path():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,140,150))
        d.rectangle([0,0,32,1], fill=(120,120,130))
        d.rectangle([0,16,32,17], fill=(120,120,130))
        d.rectangle([16,0,17,32], fill=(120,120,130))
    return f

def water():
    def f(d):
        d.rectangle([0,0,32,32], fill=(40,100,180))
        for x in range(4):
            for y in range(4):
                d.rectangle([x*8+2, y*8+4, x*8+6, y*8+6], fill=(80,150,220))
    return f

def sand():
    def f(d):
        d.rectangle([0,0,32,32], fill=(220,200,140))
        for x in range(10):
            for y in range(10):
                d.point((x*3+1, y*3+1), fill=(200,180,120))
    return f

def snow():
    def f(d):
        d.rectangle([0,0,32,32], fill=(230,240,250))
        for x in range(8):
            for y in range(8):
                d.point((x*4+2, y*4+2), fill=(200,220,240))
    return f

def lava():
    def f(d):
        d.rectangle([0,0,32,32], fill=(180,40,20))
        for x in range(3):
            for y in range(3):
                d.ellipse([x*10+2, y*10+2, x*10+8, y*10+8], fill=(255,150,30))
    return f

def swamp():
    def f(d):
        d.rectangle([0,0,32,32], fill=(60,100,40))
        for x in range(4):
            for y in range(4):
                d.ellipse([x*8+2, y*8+2, x*8+10, y*8+10], fill=(80,140,60))
    return f

def ice():
    def f(d):
        d.rectangle([0,0,32,32], fill=(180,220,255))
        d.rectangle([4,4,28,28], fill=(200,235,255))
        d.line([0,0,32,32], fill=(160,200,240), width=1)
    return f

def void_g():
    def f(d):
        d.rectangle([0,0,32,32], fill=(20,10,30))
        for x in range(10):
            for y in range(10):
                d.point((x*3+1, y*3+1), fill=(60,40,80))
    return f

# === Row 1: Walls ===
def wood_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(120,80,40))
        for i in range(4):
            d.rectangle([0, i*8, 32, i*8+2], fill=(100,60,30))
    return f

def stone_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([0,0,32,2], fill=(80,80,90))
        d.rectangle([0,15,32,17], fill=(80,80,90))
        d.rectangle([15,0,17,16], fill=(80,80,90))
    return f

def brick_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(180,80,60))
        for x in range(2):
            for y in range(4):
                d.rectangle([x*16, y*8, x*16+14, y*8+6], fill=(160,60,40))
    return f

def bamboo_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(60,140,60))
        d.rectangle([8,0,12,32], fill=(40,120,40))
        d.rectangle([20,4,24,32], fill=(40,120,40))
        for i in range(4):
            d.rectangle([4, i*8, 16, i*8+4], fill=(80,160,80))
    return f

def bamboo_dense():
    def f(d):
        d.rectangle([0,0,32,32], fill=(40,120,40))
        for x in [4,12,20,28]:
            d.rectangle([x,0,x+4,32], fill=(60,140,60))
    return f

def tomb_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,70,90))
        d.rectangle([0,0,32,2], fill=(60,50,70))
        d.rectangle([0,15,32,17], fill=(60,50,70))
        d.rectangle([15,0,17,32], fill=(60,50,70))
        d.rectangle([4,4,6,6], fill=(60,50,70))
    return f

def demon_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,30,50))
        for x in range(4):
            for y in range(4):
                d.rectangle([x*8, y*8, x*8+6, y*8+6], fill=(100,40,60))
    return f

def ice_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(160,200,240))
        d.rectangle([0,0,32,2], fill=(140,180,220))
        d.rectangle([0,15,32,17], fill=(140,180,220))
        d.ellipse([4,4,12,12], fill=(200,230,255))
    return f

def gold_wall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(200,180,80))
        d.rectangle([0,0,32,2], fill=(180,160,60))
        d.rectangle([0,15,32,17], fill=(180,160,60))
        d.ellipse([10,10,22,22], fill=(255,220,100))
    return f

def tree():
    def f(d):
        d.rectangle([0,0,32,32], fill=(60,140,60))
        d.rectangle([12,16,20,32], fill=(100,70,40))
        d.ellipse([4,2,28,20], fill=(40,120,40))
        d.ellipse([6,4,26,18], fill=(50,140,50))
    return f

# === Row 2: Decorations ===
def flowers():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        colors = [(255,100,100), (255,200,50), (200,100,255), (100,200,255)]
        for x in range(4):
            for y in range(4):
                d.ellipse([x*8+3, y*8+3, x*8+7, y*8+7], fill=colors[(x+y)%4])
    return f

def rock():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([6,10,26,24], fill=(140,140,150))
        d.ellipse([8,12,24,22], fill=(160,160,170))
    return f

def small_rock():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([4,16,12,24], fill=(140,140,150))
        d.ellipse([18,18,26,26], fill=(120,120,130))
    return f

def spring():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([4,12,28,28], fill=(60,140,200))
        d.ellipse([8,16,24,24], fill=(100,180,240))
        d.ellipse([12,20,20,22], fill=(200,230,255))
    return f

def grass_tall():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        for i in range(7):
            d.rectangle([i*4+2, 8+i*3, i*4+4, 24+i*2], fill=(60,140,40))
    return f

def bamboo_deco():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([14,0,18,32], fill=(40,120,40))
        for i in range(3):
            d.rectangle([8, i*10, 24, i*10+2], fill=(60,140,60))
    return f

def mushroom():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([14,18,18,28], fill=(220,200,180))
        d.ellipse([6,10,26,20], fill=(180,60,60))
        d.ellipse([10,12,14,16], fill=(255,255,255))
    return f

def chest():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([6,14,26,26], fill=(180,140,60))
        d.rectangle([6,14,26,20], fill=(200,160,80))
        d.rectangle([14,18,18,22], fill=(255,220,100))
    return f

def stele():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([10,4,22,28], fill=(140,140,150))
        d.rectangle([12,6,20,26], fill=(160,160,170))
        d.rectangle([14,10,18,12], fill=(120,120,130))
    return f

def lantern():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([14,0,18,16], fill=(100,70,40))
        d.ellipse([8,14,24,26], fill=(255,150,50))
        d.ellipse([10,16,22,24], fill=(255,200,100))
    return f

# === Row 3: Ground variants ===
def grass2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(70,150,50))
        for x in range(8):
            for y in range(5):
                d.rectangle([x*4+1, y*6, x*4+2, y*6+4], fill=(90,170,70))
    return f

def dirt2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,120,80))
        for x in range(8):
            for y in range(8):
                d.point((x*4+2, y*4+2), fill=(120,100,60))
    return f

def stone2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(120,120,130))
        d.rectangle([2,2,14,14], fill=(130,130,140))
        d.rectangle([16,2,30,14], fill=(130,130,140))
        d.rectangle([2,16,14,30], fill=(130,130,140))
        d.rectangle([16,16,30,30], fill=(130,130,140))
    return f

def water2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(30,80,160))
        for x in range(4):
            for y in range(8):
                d.rectangle([x*8, y*4+2, x*8+6, y*4+4], fill=(60,130,200))
    return f

def sand2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(200,180,120))
        for x in range(5):
            for y in range(5):
                d.ellipse([x*6+2, y*6+2, x*6+6, y*6+6], fill=(220,200,140))
    return f

def snow2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(220,230,240))
        for x in range(8):
            for y in range(5):
                d.rectangle([x*4+1, y*6, x*4+3, y*6+4], fill=(240,250,255))
    return f

def lava2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(160,30,10))
        for x in range(3):
            for y in range(3):
                d.ellipse([x*8+4, y*8+4, x*8+12, y*8+12], fill=(255,120,20))
    return f

def swamp2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(50,80,30))
        for x in range(3):
            for y in range(3):
                d.ellipse([x*10+2, y*10+2, x*10+10, y*10+10], fill=(70,120,50))
    return f

def ice2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(170,210,245))
        d.line([0,8,32,24], fill=(150,190,230), width=2)
        d.line([8,0,24,32], fill=(150,190,230), width=2)
    return f

def void2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(15,5,25))
        for x in range(10):
            for y in range(10):
                d.point((x*3, y*3), fill=(50,30,70))
    return f

# === Row 4: Special objects ===
def portal_left():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([4,4,28,28], fill=(100,50,200))
        d.ellipse([8,8,24,24], fill=(150,100,255))
        d.ellipse([12,12,20,20], fill=(200,180,255))
    return f

def portal_right():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([4,4,28,28], fill=(200,50,50))
        d.ellipse([8,8,24,24], fill=(255,100,100))
        d.ellipse([12,12,20,20], fill=(255,180,180))
    return f

def mirror():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,140,150))
        d.rectangle([12,4,20,28], fill=(100,70,40))
        d.ellipse([4,4,28,16], fill=(180,200,255))
        d.ellipse([6,6,26,14], fill=(220,240,255))
    return f

def cushion():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,120,80))
        d.ellipse([6,10,26,26], fill=(180,140,80))
        d.ellipse([8,12,24,24], fill=(200,160,100))
    return f

def altar_platform():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,120,80))
        d.rectangle([4,20,28,32], fill=(160,140,100))
        d.rectangle([8,12,24,20], fill=(180,160,120))
        d.rectangle([12,4,20,12], fill=(200,180,140))
    return f

def furnace():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,120,80))
        d.ellipse([8,12,24,28], fill=(120,80,40))
        d.ellipse([10,14,22,26], fill=(140,100,60))
        d.rectangle([12,8,20,12], fill=(100,60,30))
    return f

def bookshelf():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,120,80))
        d.rectangle([2,2,30,30], fill=(100,60,30))
        d.rectangle([4,4,28,12], fill=(180,60,60))
        d.rectangle([4,14,28,22], fill=(60,60,180))
        d.rectangle([4,24,28,30], fill=(60,120,60))
    return f

def altar():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([4,16,28,32], fill=(120,120,130))
        d.rectangle([8,8,24,16], fill=(140,140,150))
        d.rectangle([12,2,20,8], fill=(180,160,80))
    return f

def spirit_vein():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([4,12,28,24], fill=(100,200,255))
        d.ellipse([8,14,24,22], fill=(150,220,255))
        d.ellipse([12,16,20,20], fill=(200,240,255))
    return f

def thunder_platform():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([4,8,28,32], fill=(120,120,130))
        d.rectangle([8,4,24,8], fill=(180,180,200))
        d.rectangle([14,0,18,4], fill=(255,255,100))
    return f

# === Row 5: Buildings ===
def door():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([8,0,24,32], fill=(120,80,40))
        d.rectangle([10,2,22,30], fill=(140,100,60))
        d.rectangle([18,16,20,18], fill=(200,180,80))
    return f

def window():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([6,6,26,26], fill=(100,180,220))
        d.rectangle([15,6,17,26], fill=(80,80,90))
        d.rectangle([6,15,26,17], fill=(80,80,90))
    return f

def pillar():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([10,0,22,32], fill=(180,60,60))
        d.rectangle([12,2,20,30], fill=(200,80,80))
    return f

def roof_down():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.polygon([(0,16),(16,0),(32,16)], fill=(60,60,80))
        d.polygon([(2,16),(16,2),(30,16)], fill=(80,80,100))
    return f

def roof_up():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.polygon([(0,0),(16,16),(32,0)], fill=(60,60,80))
        d.polygon([(2,2),(16,14),(30,2)], fill=(80,80,100))
    return f

def flag():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([4,0,6,32], fill=(100,70,40))
        d.rectangle([6,2,24,12], fill=(180,60,60))
    return f

def lamp_post():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,120,80))
        d.rectangle([14,4,18,32], fill=(100,70,40))
        d.ellipse([8,0,24,10], fill=(255,200,50))
        d.ellipse([10,2,22,8], fill=(255,255,200))
    return f

def bell():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([14,0,18,8], fill=(100,70,40))
        d.ellipse([4,8,28,28], fill=(200,180,80))
        d.ellipse([6,10,26,26], fill=(220,200,100))
    return f

def well():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.ellipse([6,10,26,28], fill=(140,140,150))
        d.ellipse([10,14,22,24], fill=(60,120,180))
    return f

def bridge():
    def f(d):
        d.rectangle([0,0,32,32], fill=(40,100,180))
        d.rectangle([0,10,32,22], fill=(140,100,60))
        d.rectangle([2,12,30,18], fill=(160,120,80))
    return f

# === Row 6: Corners/Edges ===
def corner_bl():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([0,0,16,32], fill=(100,100,110))
        d.rectangle([0,0,32,16], fill=(100,100,110))
    return f

def corner_br():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([16,0,32,32], fill=(100,100,110))
        d.rectangle([0,0,32,16], fill=(100,100,110))
    return f

def corner_tl():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([0,0,16,32], fill=(100,100,110))
        d.rectangle([0,16,32,32], fill=(100,100,110))
    return f

def corner_tr():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([16,0,32,32], fill=(100,100,110))
        d.rectangle([0,16,32,32], fill=(100,100,110))
    return f

def edge_left():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([0,0,16,32], fill=(100,100,110))
    return f

def edge_right():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([16,0,32,32], fill=(100,100,110))
    return f

def edge_top():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([0,0,32,16], fill=(100,100,110))
    return f

def edge_bottom():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.rectangle([0,16,32,32], fill=(100,100,110))
    return f

def inner_corner():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([16,0,32,16], fill=(80,160,60))
    return f

def outer_corner():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.rectangle([0,16,16,32], fill=(80,160,60))
        d.rectangle([16,16,32,32], fill=(80,160,60))
    return f

# === Row 7: Extra decorations ===
def grass_tall2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(60,140,40))
        for i in range(10):
            d.rectangle([i*3+1, 6, i*3+2, 24], fill=(80,160,60))
    return f

def flowers2():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        colors = [(255,80,80), (255,220,50), (180,80,255), (80,180,255)]
        for x in range(4):
            for y in range(4):
                d.ellipse([x*8+4, y*8+4, x*8+8, y*8+8], fill=colors[(x*4+y)%4])
    return f

def vines():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        for i in range(5):
            d.rectangle([4+i*2, 0, 6+i*2, 4+i*4], fill=(60,140,40))
    return f

def cracks():
    def f(d):
        d.rectangle([0,0,32,32], fill=(140,140,150))
        d.line([4,4,28,28], fill=(100,100,110), width=2)
        d.line([16,0,20,32], fill=(100,100,110), width=1)
    return f

def moss():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        for x in range(5):
            for y in range(5):
                d.ellipse([x*6+2, y*6+2, x*6+8, y*6+8], fill=(80,140,60))
    return f

def cobweb():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,160,60))
        d.line([0,0,32,32], fill=(200,200,220), width=1)
        d.line([32,0,0,32], fill=(200,200,220), width=1)
        d.line([16,0,16,32], fill=(200,200,220), width=1)
        d.line([0,16,32,16], fill=(200,200,220), width=1)
    return f

def rune():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,100,110))
        d.polygon([(16,2),(28,10),(26,22),(6,22),(4,10)], fill=(180,160,80))
        d.polygon([(16,6),(24,12),(22,20),(8,20),(6,12)], fill=(220,200,120))
    return f

def blood_pool():
    def f(d):
        d.rectangle([0,0,32,32], fill=(80,30,30))
        d.ellipse([2,8,30,28], fill=(180,30,30))
        d.ellipse([6,12,26,24], fill=(220,50,50))
        d.ellipse([12,16,20,20], fill=(255,100,100))
    return f

def dragon_den():
    def f(d):
        d.rectangle([0,0,32,32], fill=(100,180,220))
        d.ellipse([2,8,30,28], fill=(80,160,200))
        d.ellipse([6,12,26,24], fill=(120,200,240))
        d.ellipse([12,16,20,20], fill=(200,240,255))
    return f

def stars():
    def f(d):
        d.rectangle([0,0,32,32], fill=(10,5,20))
        for x in range(8):
            for y in range(8):
                if (x+y)%2==0:
                    d.point((x*4+2, y*4+2), fill=(200,200,255))
    return f

# Build all rows
row0 = [grass, dirt, stone_path, water, sand, snow, lava, swamp, ice, void_g]
row1 = [wood_wall, stone_wall, brick_wall, bamboo_wall, bamboo_dense, tomb_wall, demon_wall, ice_wall, gold_wall, tree]
row2 = [flowers, rock, small_rock, spring, grass_tall, bamboo_deco, mushroom, chest, stele, lantern]
row3 = [grass2, dirt2, stone2, water2, sand2, snow2, lava2, swamp2, ice2, void2]
row4 = [portal_left, portal_right, mirror, cushion, altar_platform, furnace, bookshelf, altar, spirit_vein, thunder_platform]
row5 = [door, window, pillar, roof_down, roof_up, flag, lamp_post, bell, well, bridge]
row6 = [corner_bl, corner_br, corner_tl, corner_tr, edge_left, edge_right, edge_top, edge_bottom, inner_corner, outer_corner]
row7 = [grass_tall2, flowers2, vines, cracks, moss, cobweb, rune, blood_pool, dragon_den, stars]

all_rows = [row0, row1, row2, row3, row4, row5, row6, row7]

for row_idx, row in enumerate(all_rows):
    for col_idx, tile_gen in enumerate(row):
        tile = make_tile(tile_gen())
        tileset.paste(tile, (col_idx * T, row_idx * T), tile)

tileset.save(f"{TILES_DIR}/tileset.png")
print(f"✅ tileset.png: {sheet_w}x{sheet_h} (80 tiles, 10×8 grid)")

# Verify
from PIL import Image
img = Image.open(f"{TILES_DIR}/tileset.png")
print(f"  Size: {img.size}, Mode: {img.mode}")
