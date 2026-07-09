[app]

title = My Speech App
package.name = myapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

requirements = python3,kivy,pyjnius,android,audiostream,openssl,setuptools,cython,python-bidi,arabic-reshaper

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0

android.permissions = INTERNET, RECORD_AUDIO
android.api = 30
android.minapi = 21
android.ndk = 25c

[buildozer]

log_level = 2
warn_on_root = 1
