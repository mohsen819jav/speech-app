import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from bidi.algorithm import get_display
import arabic_reshaper

# ==================== تنظیمات فونت فارسی ====================
try:
    resource_add_path(os.path.dirname(__file__))
    LabelBase.register(name="PersianFont", fn_regular="Vazir.ttf")
    FONT_NAME = "PersianFont"
except:
    FONT_NAME = "Arial"
    print("Vazir font not found, using Arial")

def reshape_persian_text(text):
    """تبدیل متن فارسی به شکل چسبیده و راست‌چین"""
    if not text:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        rtl_text = get_display(reshaped)
        return rtl_text
    except:
        return text

# ==================== کلاس تشخیص گفتار با Android ====================
class AndroidSpeechRecognizer:
    def __init__(self):
        self.is_listening = False
        self.text_queue = []
        self.raw_text = ""
        
    def start_listening(self):
        """شروع تشخیص گفتار با استفاده از سرویس اندروید"""
        if self.is_listening:
            return
            
        try:
            from android.permissions import request_permissions, Permission
            from jnius import autoclass, cast
            from android.activity import activity
            
            # درخواست مجوزها
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.INTERNET
            ])
            
            # تنظیمات تشخیص گفتار
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            Intent = autoclass('android.content.Intent')
            
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                           RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "fa-IR")  # فارسی
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "صحبت کنید...")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)
            
            # شروع تشخیص
            activity.startActivityForResult(intent, 1001)
            self.is_listening = True
            print("🎤 تشخیص گفتار شروع شد...")
            
        except Exception as e:
            print(f"❌ خطا در شروع تشخیص: {e}")
            self.is_listening = False
            
    def stop_listening(self):
        """توقف تشخیص گفتار"""
        self.is_listening = False
        print("⏹️ تشخیص گفتار متوقف شد")
    
    def process_result(self, requestCode, resultCode, data):
        """پردازش نتیجه تشخیص گفتار"""
        if requestCode == 1001 and resultCode == -1:  # RESULT_OK
            try:
                RecognizerIntent = autoclass('android.speech.RecognizerIntent')
                results = data.getStringArrayListExtra(
                    RecognizerIntent.EXTRA_RESULTS
                )
                if results and results.size() > 0:
                    text = results.get(0)  # بهترین نتیجه
                    if text:
                        self.text_queue.append(text)
                        print(f"✅ متن تشخیص داده شد: {text}")
                        return text
            except Exception as e:
                print(f"❌ خطا در پردازش نتیجه: {e}")
        return None

# ==================== رابط کاربری اصلی ====================
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 8

        # عنوان
        title = Label(
            text="🎤 تبدیل گفتار به متن",
            font_size='18sp',
            size_hint_y=0.06,
            color=(0.2, 0.6, 1, 1),
            font_name=FONT_NAME
        )
        self.add_widget(title)

        # اسکرول ویو برای نمایش متن
        self.scroll = ScrollView(size_hint_y=0.70)
        self.text_label = Label(
            text=reshape_persian_text("برای شروع دکمه را بزنید..."),
            font_size='20sp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            color=(1, 1, 1, 1),
            font_name=FONT_NAME
        )
        self.text_label.bind(size=self.text_label.setter('text_size'))
        self.scroll.add_widget(self.text_label)
        self.add_widget(self.scroll)

        # دکمه Start/Stop
        self.btn_start = Button(
            text="🎤 شروع",
            font_size='16sp',
            size_hint_y=0.08,
            background_color=(0, 0.7, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_start.bind(on_press=self.toggle_listening)
        self.add_widget(self.btn_start)

        # دکمه Clear
        btn_clear = Button(
            text="🗑️ پاک کردن",
            font_size='14sp',
            size_hint_y=0.07,
            background_color=(0.7, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_clear.bind(on_press=self.clear_text)
        self.add_widget(btn_clear)

        # دکمه تست (برای تست تشخیص)
        btn_test = Button(
            text="🧪 تست میکروفون",
            font_size='14sp',
            size_hint_y=0.06,
            background_color=(0.3, 0.3, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        btn_test.bind(on_press=self.test_microphone)
        self.add_widget(btn_test)

        # متغیرها
        self.recognizer = AndroidSpeechRecognizer()
        self.is_listening = False
        self.raw_text = ""
        
        # بروزرسانی هر ۰٫۵ ثانیه
        Clock.schedule_interval(self.update_text, 0.5)

    def test_microphone(self, instance):
        """تست میکروفون و مجوزها"""
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])
            self.text_label.text = reshape_persian_text("✅ مجوزها دریافت شدند!\nحالا دکمه شروع را بزنید.")
        except Exception as e:
            self.text_label.text = reshape_persian_text(f"❌ خطا: {str(e)}")

    def toggle_listening(self, instance):
        """شروع یا توقف تشخیص گفتار"""
        if not self.is_listening:
            self.recognizer.start_listening()
            self.is_listening = True
            self.btn_start.text = "⏹️ توقف"
            self.btn_start.background_color = (0.9, 0.2, 0.2, 1)
            self.raw_text = "🎤 در حال گوش دادن...\n"
            self.text_label.text = reshape_persian_text(self.raw_text)
        else:
            self.recognizer.stop_listening()
            self.is_listening = False
            self.btn_start.text = "🎤 شروع"
            self.btn_start.background_color = (0, 0.7, 0.2, 1)

    def update_text(self, dt):
        """بروزرسانی متن نمایش داده شده"""
        if self.is_listening and self.recognizer.text_queue:
            for text in self.recognizer.text_queue:
                self.raw_text += text + "\n"
            self.recognizer.text_queue = []  # پاک کردن صف
            
            # محدود کردن به ۲۰ خط آخر
            lines = self.raw_text.split('\n')
            if len(lines) > 20:
                lines = lines[-20:]
                self.raw_text = '\n'.join(lines)
            
            # نمایش با فرمت فارسی
            display_text = reshape_persian_text(self.raw_text)
            self.text_label.text = display_text
            self.scroll.scroll_y = 0

    def clear_text(self, instance):
        """پاک کردن متن"""
        self.raw_text = ""
        self.text_label.text = reshape_persian_text("متن پاک شد.\nبرای شروع دکمه را بزنید...")

class SpeechApp(App):
    def build(self):
        return MainLayout()

    def on_start(self):
        """هنگام شروع اپلیکیشن"""
        print("✅ برنامه شروع شد")

    def on_stop(self):
        """هنگام بستن اپلیکیشن"""
        if hasattr(self, 'root') and self.root.is_listening:
            self.root.recognizer.stop_listening()

if __name__ == '__main__':
    SpeechApp().run() 
