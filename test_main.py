"""Minimal test - just pygame init and a black screen."""
import sys
import os

print("[TEST] Starting minimal test app...")

# Install crash handler
def crash_handler(exc_type, exc_value, exc_tb):
    import traceback
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("=" * 60)
    print("[TEST CRASH]")
    print(msg)
    print("=" * 60)

sys.excepthook = crash_handler

print("[TEST] Importing pygame...")
import pygame

print("[TEST] Calling pygame.init()...")
try:
    pygame.init()
    print("[TEST] pygame.init() SUCCESS")
except Exception as e:
    print(f"[TEST] pygame.init() FAILED: {e}")
    sys.exit(1)

print("[TEST] Setting display mode...")
try:
    screen = pygame.display.set_mode((800, 480), 0)
    print("[TEST] set_mode SUCCESS")
except Exception as e:
    print(f"[TEST] set_mode FAILED: {e}")
    sys.exit(1)

print("[TEST] Filling screen red...")
try:
    screen.fill((255, 0, 0))
    pygame.display.flip()
    print("[TEST] Display updated!")
except Exception as e:
    print(f"[TEST] Display update FAILED: {e}")

print("[TEST] Entering main loop...")
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    clock.tick(30)

print("[TEST] Exiting...")
pygame.quit()
