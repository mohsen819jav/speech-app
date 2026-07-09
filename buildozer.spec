[app]

title = Speech to Text
package.name = speechapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

# ✅ کتابخانه‌های صحیح برای اندروید
requirements = python3==3.11.0,kivy==2.2.1,arabic-reshaper,python-bidi

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0

# ✅ مجوزهای صحیح
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25c
android.sdk = 33
android.enable_androidx = True
android.gradle_dependencies = 

# ✅ اضافه کردن برای جلوگیری از خطاهای احتمالی
android.add_src = 
android.add_activity = 
android.override_activity = 
android.arch = arm64-v8a, armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1
