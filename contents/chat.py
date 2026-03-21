from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp

class ChatScreen(MDScreen):
    def send_message(self, text_field, chat_list, scroll_view):
        user_text = text_field.text.strip()
        if not user_text: return
        
        text_field.text = "" 
        self.chat_bubble(user_text, "user", chat_list, scroll_view)
        Clock.schedule_once(lambda dt: self.bot_reply(user_text, chat_list, scroll_view), 0.5)

    def bot_reply(self, original_text, chat_list, scroll_view):
        app = MDApp.get_running_app()
        response = f"Hello {app.user_name}, I received: '{original_text}'"
        self.chat_bubble(response, "bot", chat_list, scroll_view)

    def chat_bubble(self, text, sender, chat_list, scroll_view):
        app = MDApp.get_running_app()
        is_user = sender == "user"
        
        bg_color = (0, 0, 0, 1) if is_user else (0.9, 0.9, 0.9, 1)
        font_color = (1, 1, 1, 1) if is_user else (0, 0, 0, 1)
        
        user_initial = app.user_name[0].upper() if app.user_name else "U"
        avatar_letter = user_initial if is_user else "R"
        
        row = MDBoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            adaptive_height=True, 
            spacing="10dp", 
            padding="5dp",
            opacity=0
        )
        
        avatar = MDCard(
            size_hint=(None, None), size=(dp(40), dp(40)), 
            radius=[dp(20)]*4, md_bg_color=bg_color, pos_hint={"top": 1}
        )
        avatar.add_widget(MDLabel(text=avatar_letter, halign="center", theme_text_color="Custom", text_color=font_color))
        
        bubble = MDCard(
            orientation="vertical",
            size_hint_x=0.7,
            size_hint_y=None, 
            adaptive_height=True,
            md_bg_color=bg_color, 
            padding="12dp", radius=[dp(15)]*4
        )
        
        lbl = MDLabel(text=text, theme_text_color="Custom", text_color=font_color, adaptive_height=True)
        bubble.add_widget(lbl)
        
        spacer = Widget(size_hint_x=0.2)

        if is_user:
            row.add_widget(spacer); row.add_widget(bubble); row.add_widget(avatar)
        else:
            row.add_widget(avatar); row.add_widget(bubble); row.add_widget(spacer)

        chat_list.add_widget(row)
        Clock.schedule_once(lambda dt: setattr(scroll_view, 'scroll_y', 0), 0.1)
        Animation(opacity=1, duration=0.3).start(row)