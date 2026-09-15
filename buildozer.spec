[app]

title = Ahmed World
package.name = ahmedworld
package.domain = org.ahmedapp

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,wav,mp3,ttf,otf
source.exclude_dirs = tests,bin,venv,.buildozer,.git,__pycache__

version = 2.0

icon.filename = %(source.dir)s/app_icon.png

requirements = python3,kivy==2.1.0,plyer,arabic-reshaper,pillow

p4a.branch = v2024.01.21
p4a.bootstrap = sdl2

orientation = portrait
fullscreen = 1

android.permissions = VIBRATE,INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 0
