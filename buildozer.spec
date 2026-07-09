[app]
 
title = Speech to Text
package.name = speechapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

# ⚠️ فقط کتابخانه‌های ضروری (بدون pyaudio و vosk)
requirements = python3==3.11.0,kivy==2.2.1,arabic-reshaper,python-bidi==0.4.2

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0

# مجوزهای اندروید
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25c
android.sdk = 33
android.enable_androidx = True

[buildozer]

log_level = 2
warn_on_root = 1
