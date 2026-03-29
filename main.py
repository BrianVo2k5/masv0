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
from contents.chat import ChatScreen
from kivy.factory import Factory
from file_upload import FileUploadManager
from kivymd.uix.label import MDLabel

Factory.register("ChatScreen", cls=ChatScreen)

Window.size = (1600, 900)
Config.set('graphics', 'resizable', False)

class MainRoot(FloatLayout):
    pass

class ChatApp(MDApp):
    reveal_radius = NumericProperty(0) 
    user_uuid = str(uuid.uuid4())
    user_name = StringProperty("buddy") 
    bot_name = StringProperty("researchr.masv0")
    bot_description = StringProperty("Your friendly neighborhood summarizer.")

    def build(self):
        self.title = "researchr.masv0"
        
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.file_manager = FileUploadManager(self.handle_uploaded_text)

        if os.path.exists("app_fonts/JetBrainsMono-Regular.ttf"):
            LabelBase.register(
                name="JetBrains Mono", 
                fn_regular="app_fonts/JetBrainsMono-Regular.ttf"
            )
        
        Builder.load_file("app.kv")
        
        Clock.schedule_once(self.start_reveal_animation, 0.2)
        
        return MainRoot()

    def switch_to_chat(self, name):
        if name.strip():
            self.user_name = name.strip()
        
        sm = self.root.ids.screen_manager
        sm.transition.direction = "left"
        sm.current = "chat"

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

        preview = text[:500]

        chat_list.add_widget(
            MDLabel(
                text=f"[b]📂 Uploaded file:[/b]\n{preview}",
                markup=True,
                size_hint_y=None,
                height="100dp"
            )
        )

        # auto scroll to newest message
        Clock.schedule_once(lambda dt: scroll_view.scroll_to(chat_list.children[0]))

if __name__ == '__main__':
    ChatApp().run()