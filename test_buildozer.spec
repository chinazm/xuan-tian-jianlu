[app]
title = Test
package.name = test_pygame
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,ogg,wav,mp3
version = 0.1
android.numeric_version = 1
android.presplash_color = #1a1a2e
android.wakelock = True
orientation = landscape
fullscreen = 1
android.permissions = android.permission.VIBRATE
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer_test
bin_dir = ./bin_test
