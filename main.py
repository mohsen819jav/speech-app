import vosk
import json
import threading
import queue
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

# Register Persian font
try:
    resource_add_path(os.path.dirname(__file__))
    LabelBase.register(name="PersianFont", fn_regular="Vazir.ttf")
    FONT_NAME = "PersianFont"
except:
    FONT_NAME = "Arial"
    print("Vazir font not found, using Arial")


def reshape_persian_text(text):
    if not text:
        return text
    reshaped = arabic_reshaper.reshape(text)
    rtl_text = get_display(reshaped)
    return rtl_text


class SpeechRecognizer:
    def __init__(self, model_path="vosk-model-small-fa-0.5"):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.text_queue = queue.Queue()
        try:
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            print("Model loaded")
        except Exception as e:
            print(f"Error: {e}")

    def start_listening(self):
        if self.is_listening:
            return
        try:
            import pyaudio
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000
            )
            self.is_listening = True
            print("Listening...")
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            print(f"Error: {e}")

    def _listen_loop(self):
        while self.is_listening:
            try:
                data = self.stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self.text_queue.put(text)
            except:
                break

    def stop_listening(self):
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("Stopped")

    def get_text(self):
        texts = []
        while not self.text_queue.empty():
            try:
                texts.append(self.text_queue.get_nowait())
            except:
                break
        return texts


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 8

        # Title - smaller for mobile
        title = Label(
            text="Speech to Text",
            font_size='16sp',
            size_hint_y=0.06,
            color=(0.2, 0.6, 1, 1),
            font_name=FONT_NAME
        )
        self.add_widget(title)

        # Scroll view with smaller text for mobile
        self.scroll = ScrollView(size_hint_y=0.75)
        self.text_label = Label(
            text="Press Start and speak...",
            font_size='18sp',
            halign='left',
            valign='top',
            text_size=(None, None),
            color=(1, 1, 1, 1),
            font_name=FONT_NAME
        )
        self.text_label.bind(size=self.text_label.setter('text_size'))
        self.scroll.add_widget(self.text_label)
        self.add_widget(self.scroll)

        # Start button - smaller for mobile
        self.btn_start = Button(
            text="Start",
            font_size='14sp',
            size_hint_y=0.09,
            background_color=(0, 0.7, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_start.bind(on_press=self.toggle_listening)
        self.add_widget(self.btn_start)

        # Clear button - smaller for mobile
        btn_clear = Button(
            text="Clear",
            font_size='12sp',
            size_hint_y=0.07,
            background_color=(0.7, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_clear.bind(on_press=self.clear_text)
        self.add_widget(btn_clear)

        self.recognizer = SpeechRecognizer()
        self.is_listening = False
        self.raw_text = ""
        Clock.schedule_interval(self.update_text, 0.5)

    def toggle_listening(self, instance):
        if not self.is_listening:
            self.recognizer.start_listening()
            self.is_listening = True
            self.btn_start.text = "Stop"
            self.btn_start.background_color = (0.9, 0.2, 0.2, 1)
            self.raw_text = "Listening...\n"
            self.text_label.text = self.raw_text
        else:
            self.recognizer.stop_listening()
            self.is_listening = False
            self.btn_start.text = "Start"
            self.btn_start.background_color = (0, 0.7, 0.2, 1)

    def update_text(self, dt):
        if self.is_listening:
            texts = self.recognizer.get_text()
            if texts:
                for t in texts:
                    self.raw_text += t + "\n"
                # Keep only last 20 lines for mobile
                lines = self.raw_text.split('\n')
                if len(lines) > 20:
                    lines = lines[-20:]
                    self.raw_text = '\n'.join(lines)
                display_text = reshape_persian_text(self.raw_text)
                self.text_label.text = display_text
                self.scroll.scroll_y = 0

    def clear_text(self, instance):
        self.raw_text = "Text cleared.\n"
        self.text_label.text = self.raw_text


class SpeechApp(App):
    def build(self):
        return MainLayout()

    def on_stop(self):
        if hasattr(self, 'root') and self.root.is_listening:
            self.root.recognizer.stop_listening()


if __name__ == '__main__':
    SpeechApp().run()
 