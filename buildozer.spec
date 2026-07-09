[app]

title = Speech to Text
package.name = speechapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

requirements = python3==3.11.0,kivy==2.2.1,arabic-reshaper,python-bidi==0.4.2

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO
android.api = 30
android.minapi = 21
android.ndk = 25c
android.sdk = 30
android.enable_androidx = True

[buildozer]

log_level = 2
warn_on_root = 1
