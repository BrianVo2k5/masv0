import threading
from datetime import datetime
import gspread
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
# IMPORTANT! BART-LARGE-CNN IS INTRODUCED HERE IN ORDER TO TEST OUT THE FUNCTIONS!
import torch
from transformers import pipeline
summarizer = pipeline("summarization",model="facebook/bart-large-cnn")


class FeedbackContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.adaptive_height = True 
        
        self.ratings = {
            "Accuracy": 0,
            "Length": 0,
            "Legibility": 0,
            "Tone": 0,
            "Quality": 0
        }
        self.star_buttons = {}
        
        for param in self.ratings.keys():
            row = self.create_rating_row(param)
            self.add_widget(row)
        
        self.feedback_input = MDTextField(
            hint_text="Tell us how we did...",
            font_name="JetBrains Mono",
            max_text_length=100,
            multiline=True
        )
        self.add_widget(self.feedback_input)
        
        consent_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing="10dp")
        
        self.consent_checkbox = MDCheckbox(
            size_hint=(None, None), 
            size=("48dp", "48dp")
        )
        
        self.consent_label = MDLabel(
            text="* I consent to sending prompt, response, and feedback to servers.",
            theme_text_color="Hint",
            font_name="JetBrains Mono",
            adaptive_height=True
        )
        
        consent_layout.add_widget(self.consent_checkbox)
        consent_layout.add_widget(self.consent_label)
        
        self.add_widget(consent_layout)

    def create_rating_row(self, param_name):
        row_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing="10dp")
        label = MDLabel(text=param_name, font_name="JetBrains Mono", size_hint_x=0.4, theme_text_color="Secondary")
        row_layout.add_widget(label)
        
        stars_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing="2dp", size_hint_x=0.6)
        self.star_buttons[param_name] = []
        
        for i in range(1, 6):
            star = MDIconButton(
                icon="star-outline", 
                on_release=lambda x, p=param_name, val=i: self.set_rating(p, val)
            )
            self.star_buttons[param_name].append(star)
            stars_layout.add_widget(star)
            
        row_layout.add_widget(stars_layout)
        return row_layout

    def set_rating(self, param_name, value):
        self.ratings[param_name] = value
        for i, star in enumerate(self.star_buttons[param_name]):
            star.icon = "star" if i < value else "star-outline"


class ChatScreen(MDScreen):
    dialog = None 

    def send_message(self, text_field, chat_list, scroll_view):
        user_text = text_field.text.strip()
        if not user_text: return
        
        text_field.text = "" 
        self.chat_bubble(user_text, "user", chat_list, scroll_view)
        Clock.schedule_once(lambda dt: self.bot_reply(user_text, chat_list, scroll_view), 0.5)

    def bot_reply(self, original_text, chat_list, scroll_view):
        if len(original_text.strip()) < 100:
            self.chat_bubble("Please provide more text!", "bot", chat_list, scroll_view)
            return

    # 1. Create the bubble and get the label reference
        base_text = "Hang tight, I'm working on it"
        thinking_label = self.chat_bubble(f"{base_text}...", "bot", chat_list, scroll_view, original_prompt=original_text)

    # 2. Define the animation logic
        def shift_dots(dt):
        # Count current dots
            curr_dots = thinking_label.text.count(".")
            if curr_dots >= 3:
                thinking_label.text = base_text + "."
            else:
                thinking_label.text = base_text + "." * (curr_dots + 1)

    # 3. Start the animation (runs every 0.5 seconds)
    # We store this in a variable so we can stop it later!
        anim_event = Clock.schedule_interval(shift_dots, 0.5)

        def generate_summary():
            try:
                raw_output = summarizer(original_text, max_length=200, min_length=100, do_sample=False)
                final_text = raw_output[0]['summary_text']
            except Exception as e:
                final_text = f"Error: {str(e)}"
        
        # 4. Pass the final text AND the animation event to the UI update
            Clock.schedule_once(lambda dt: update_ui(final_text), 0)

        def update_ui(final_text):
            # STOP the dot animation
            anim_event.cancel()
        
        # Show the actual AI result
            if thinking_label:
                thinking_label.text = final_text
                thinking_label.texture_update()

        threading.Thread(target=generate_summary, daemon=True).start()

    def chat_bubble(self, text, sender, chat_list, scroll_view, original_prompt=""):
        app = MDApp.get_running_app()
        is_user = sender == "user"
        
        bg_color = (0, 0, 0, 1) if is_user else (0.9, 0.9, 0.9, 1)
        font_color = (1, 1, 1, 1) if is_user else (0, 0, 0, 1)
        
        user_initial = app.user_name[0].upper() if app.user_name else "U"
        avatar_letter = user_initial if is_user else "Re"
        
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
        
        # Create the label
        lbl = MDLabel(text=text, theme_text_color="Custom", text_color=font_color, adaptive_height=True)
        bubble.add_widget(lbl)
        
        spacer = Widget(size_hint_x=0.2)

        if is_user:
            row.add_widget(spacer); row.add_widget(bubble); row.add_widget(avatar)
        else:
            feedback_btn = MDIconButton(
                icon="comment", 
                icon_size="20sp",
                pos_hint={"center_y": 0.5},
                # FIX: We use 'lbl.text' so it captures the LATEST text when clicked, not the initial text
                on_release=lambda x: self.show_feedback_dialog(original_prompt, lbl.text)
            )
            row.add_widget(avatar)
            row.add_widget(bubble)
            row.add_widget(feedback_btn) 
            row.add_widget(spacer)

        chat_list.add_widget(row)
        Clock.schedule_once(lambda dt: setattr(scroll_view, 'scroll_y', 0), 0.1)
        Animation(opacity=1, duration=0.3).start(row)
        
        # CRITICAL FIX: Return the label widget so bot_reply can update it later
        return lbl

    def show_feedback_dialog(self, prompt_text, bot_response):
        self.feedback_content = FeedbackContent()
        
        self.submit_btn = MDFlatButton(
            text="SUBMIT",
            disabled=True, 
            theme_text_color="Hint", 
            on_release=lambda x: self.submit_feedback(prompt_text, bot_response)
        )
        
        self.dialog = MDDialog(
            title="Rate this response",
            type="custom",
            content_cls=self.feedback_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                self.submit_btn 
            ],
        )
        
        self.feedback_content.consent_checkbox.bind(active=self.toggle_submit_button)
        self.dialog.open()

    def toggle_submit_button(self, checkbox_instance, is_active):
        self.submit_btn.disabled = not is_active
        if is_active:
            self.submit_btn.theme_text_color = "Primary" 
        else:
            self.submit_btn.theme_text_color = "Hint"    

    def submit_feedback(self, prompt_text, bot_response):
        app = MDApp.get_running_app()
        ratings_dict = self.feedback_content.ratings 
        feedback_text = self.feedback_content.feedback_input.text

        user_uuid = getattr(app, 'user_uuid', "Unknown_UUID")
        
        # 1. Dismiss the dialog immediately so the user doesn't have to wait
        self.dialog.dismiss()
        
        # 2. Start a background thread to upload the data to Google Sheets
        threading.Thread(
            target=self._upload_to_sheets_worker,
            args=(prompt_text, bot_response, ratings_dict, feedback_text, user_uuid),
            daemon=True
        ).start()

    def _upload_to_sheets_worker(self, prompt_text, bot_response, ratings_dict, feedback_text, user_uuid):
        """This runs in the background to prevent freezing the UI."""
        try:

            gc = gspread.service_account(filename="credentials.json")
            
            sheet = gc.open_by_key("1nmiDOoYGxnxlJ5v0fxGJqF0i2LzaVJSHKzcTEIAoawQ").sheet1 
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row_data = [
                timestamp,
                user_uuid,
                prompt_text,
                bot_response,
                ratings_dict.get("Accuracy", 0),
                ratings_dict.get("Length", 0),
                ratings_dict.get("Legibility", 0),
                ratings_dict.get("Tone", 0),
                ratings_dict.get("Quality", 0),
                feedback_text
            ]
            
            # Append the row to the next empty line in the sheet
            sheet.append_row(row_data)
            print("Successfully uploaded feedback to Google Sheets!")
            
        except Exception as e:
            print(f"Failed to upload to Google Sheets: {e}")