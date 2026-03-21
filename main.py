import os
from kivymd.app import MDApp
import asyncio
from kaki.app import App 
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.properties import NumericProperty, StringProperty
from kivy.core.window import Window
from kivy.animation import Animation
from contents.chat import ChatScreen
from kivy.core.window import Window

# Set the window size (width, height)
Window.size = (1600, 900) 

from kivy.config import Config
Config.set('graphics', 'resizable', False)

class MainRoot(FloatLayout):
    pass

class ChatApp(App, MDApp):
    DEBUG = 1
    KV_FILES = {os.path.join(os.getcwd(), "app.kv")}
    AUTORELOADER_PATHS = [(".", {"recursive": True})]

    reveal_radius = NumericProperty(0) 
    user_name = StringProperty("buddy") 
    bot_name = StringProperty("researchr.masv0")
    bot_description = StringProperty("Your friendly neighboorhood summarizer.")

    def build_app(self):
        self.title = "researchr.masv0" 
        
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light" 
        
        LabelBase.register(
            name="JetBrains Mono", 
            fn_regular="app_fonts/JetBrainsMono-Regular.ttf"
        )
        
        for style in self.theme_cls.font_styles:
            if style not in ["Icon", "Icons"]:
                self.theme_cls.font_styles[style][0] = "JetBrains Mono"
        
        Clock.schedule_once(self.start_reveal_animation, 0.2)
        
        return MainRoot()

        for style in self.theme_cls.font_styles:
            if style not in ["Icon", "Icons"]:
                self.theme_cls.font_styles[style][0] = "JetBrains Mono"
        
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

    def start_reveal_animation(self, dt):
        max_radius = (Window.width**2 + Window.height**2)**0.5
        anim = Animation(reveal_radius=max_radius, duration=10, t='out_expo')
        anim.start(self)

if __name__ == '__main__':
    ChatApp().run()