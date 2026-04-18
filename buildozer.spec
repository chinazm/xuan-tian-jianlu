[app]

# (str) Title of your application
title = 玄天剑录

# (str) Package name
package.name = xianxia_rpg

# (str) Package domain (needed for android/ios packaging)
package.domain = org.gaorong

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf,ogg,wav,mp3

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Pygame is supported in recent python-for-android versions
requirements = python3,pygame

# (str) Custom source folders for requirements
# requirements.source.pygame = ../../pygame

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Android application version code
android.numeric_version = 1

# (str) Presplash background color (修仙主题深色背景)
android.presplash_color = #1a1a2e

# (str) Wakelock (prevent screen from sleeping during gameplay)
android.wakelock = True

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (string) Presplash background color
#android.presplash_color = #000000

# (list) Permissions
android.permissions = android.permission.VIBRATE

# (str) Android NDK version
#android.ndk = 25b

# (str) Android API level
android.api = 33
android.minapi = 21
#android.sdk = 20
#android.ndk_api = 21

# (str) Path to specific Python executable
#python.host =

# (str) Python version to use
#python_version = 3

# (list) P4A bootstrap to use
#p4a.bootstrap = sdl2

# (list) Add extra Java arguments to P4A
#p4a.extra_args =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk) storage
bin_dir = ./bin
