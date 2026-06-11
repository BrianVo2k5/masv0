import os 
import uuid
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.properties import NumericProperty, StringProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.config import Config
from contents.chat import ChatScreen, set_active_model, set_output_tokens, set_max_attempts
import contents.settings as app_settings
from kivy.factory import Factory
from file_upload import FileUploadManager
from kivymd.uix.label import MDLabel
from kivymd.toast import toast

Factory.register("ChatScreen", cls=ChatScreen)

Window.size = (1600, 900)
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,disable_multitouch')

class MainRoot(FloatLayout):
    pass

class ChatApp(MDApp):
    reveal_radius = NumericProperty(0)
    user_uuid = str(uuid.uuid4())
    user_name = StringProperty("buddy")
    active_model = StringProperty(app_settings.ACTIVE_MODEL)
    bot_name = StringProperty("researchr.masv0")
    bot_description = StringProperty("Your friendly neighborhood summarizer.")

    output_tokens        = NumericProperty(0)
    output_tokens_min    = NumericProperty(0)
    output_tokens_max    = NumericProperty(0)
    active_max_new_tokens = NumericProperty(0)  # live value shown in chat indicator
    max_attempts         = NumericProperty(2)

    def build(self):
        self.title = "researchr.masv0"

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.file_manager = FileUploadManager(self.handle_uploaded_text)

        self._sync_generation_props(app_settings.ACTIVE_MODEL)

        if os.path.exists("app_fonts/JetBrainsMono-Regular.ttf"):
            LabelBase.register(
                name="JetBrains Mono", 
                fn_regular="app_fonts/JetBrainsMono-Regular.ttf"
            )

        for style in self.theme_cls.font_styles:
            if style not in ["Icon", "Icons"]:
                self.theme_cls.font_styles[style][0] = "JetBrains Mono"
        
        Builder.load_file("app.kv")
        
        Clock.schedule_once(self.start_reveal_animation, 0.2)
        
        return MainRoot()

    def get_manager(self):
        if self.root and 'screen_manager' in self.root.ids:
            return self.root.ids.screen_manager
            
        for widget in Window.children:
            for child in widget.walk():
                if hasattr(child, 'id') and child.id == 'screen_manager':
                    return child
                if 'ScreenManager' in str(type(child)):
                    return child
        return None

    def switch_to_chat(self, name):
        if name.strip():
            self.user_name = name.strip()
        
        sm = self.get_manager()
        if sm:
            sm.transition.direction = "left"
            sm.current = "chat"
        
    def switch_to_settings(self):
        sm = self.get_manager()
        if sm:
            sm.transition.direction = "left"
            sm.current = "settings"

    def go_back_to_chat(self):
        sm = self.get_manager()
        if sm:
            sm.transition.direction = "right"
            sm.current = "chat"

    def switch_model(self, key: str):
        set_active_model(key)
        self.active_model = key
        self._sync_generation_props(key)
        toast(f"Model: {app_settings.MODEL_DISPLAY_NAMES.get(key, key)}")

    def _sync_generation_props(self, key: str):
        gen = app_settings.MODEL_GENERATION[key]
        self.output_tokens_min    = gen["min_length"]
        self.output_tokens_max    = gen["max_new_tokens"]
        self.output_tokens        = gen["optimal"]
        self.active_max_new_tokens = gen["optimal"]

    def on_output_tokens_change(self, value: float):
        set_output_tokens(int(value))
        self.active_max_new_tokens = app_settings.ACTIVE_MAX_NEW_TOKENS

    def adjust_max_attempts(self, delta: int):
        new_val = max(1, min(5, self.max_attempts + delta))
        self.max_attempts = new_val
        set_max_attempts(new_val)

    def start_reveal_animation(self, dt):
        max_radius = (Window.width**2 + Window.height**2)**0.5
        Animation(reveal_radius=max_radius, duration=2).start(self)
    def open_file(self):
        self.file_manager.open_file_dialog()

    def handle_uploaded_text(self, text):
        print("File loaded!")

        screen = self.root.ids.screen_manager.get_screen("chat")
        chat_list = screen.ids.chat_list
        scroll_view = screen.ids.scroll_view

        screen.handle_file_upload(text, chat_list, scroll_view)

        # auto scroll to newest message
        Clock.schedule_once(lambda dt: scroll_view.scroll_to(chat_list.children[0]))

if __name__ == '__main__':
    ChatApp().run()