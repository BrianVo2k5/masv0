import threading
import re
from datetime import datetime

import torch
import gspread

from transformers import (
    pipeline,
    AutoModelForSeq2SeqLM,
    AutoTokenizer
)

from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox


# =========================================================
# MODEL SETUP
# =========================================================

# IMPORTANT:
# Use the SAME base model used during training
base_model_name = "facebook/bart-large"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_model_name)

print("Loading base model...")
model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)

print("Loading checkpoint...")
ckpt = torch.load(
    "Train/runs/model.pt",
    map_location="cpu"
)

# SAFER LOADING
missing, unexpected = model.load_state_dict(
    ckpt["model_state_dict"],
    strict=False
)

print("\n========== MODEL LOAD REPORT ==========")
print(f"Missing keys: {len(missing)}")
print(f"Unexpected keys: {len(unexpected)}")

if missing:
    print("\nMissing:")
    for k in missing[:20]:
        print(k)

if unexpected:
    print("\nUnexpected:")
    for k in unexpected[:20]:
        print(k)

print("=======================================\n")

model.eval()

# Create summarization pipeline
summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer,
    framework="pt"
)


# =========================================================
# FEEDBACK CONTENT
# =========================================================

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

        consent_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing="10dp"
        )

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

        row_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing="10dp"
        )

        label = MDLabel(
            text=param_name,
            font_name="JetBrains Mono",
            size_hint_x=0.4,
            theme_text_color="Secondary"
        )

        row_layout.add_widget(label)

        stars_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing="2dp",
            size_hint_x=0.6
        )

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


# =========================================================
# CHAT SCREEN
# =========================================================

class ChatScreen(MDScreen):

    dialog = None

    # -----------------------------------------------------
    # COPY TO CLIPBOARD
    # -----------------------------------------------------

    def on_label_click(self, instance, touch):

        if instance.collide_point(*touch.pos):

            Clipboard.copy(instance.text)
            toast("Text copied to clipboard")

    # -----------------------------------------------------
    # SEND MESSAGE
    # -----------------------------------------------------

    def send_message(self, text_field, chat_list, scroll_view):

        user_text = text_field.text.strip()

        if not user_text:
            return

        text_field.text = ""

        self.chat_bubble(
            user_text,
            "user",
            chat_list,
            scroll_view
        )

        Clock.schedule_once(
            lambda dt: self.bot_reply(
                user_text,
                chat_list,
                scroll_view
            ),
            0.5
        )

    # -----------------------------------------------------
    # FILE UPLOAD
    # -----------------------------------------------------

    def handle_file_upload(
        self,
        extracted_text,
        chat_list,
        scroll_view
    ):

        toast("📎 Document uploaded successfully!")

        self.bot_reply(
            extracted_text,
            chat_list,
            scroll_view
        )

    # -----------------------------------------------------
    # BOT REPLY
    # -----------------------------------------------------

    def bot_reply(
        self,
        original_text,
        chat_list,
        scroll_view
    ):

        if len(original_text.strip()) < 100:

            self.chat_bubble(
                "Please provide more text!",
                "bot",
                chat_list,
                scroll_view
            )

            return

        # Thinking bubble
        base_text = "Hang tight, I'm working on it"

        thinking_label = self.chat_bubble(
            f"{base_text}...",
            "bot",
            chat_list,
            scroll_view,
            original_prompt=original_text
        )

        # Animated dots
        def shift_dots(dt):

            curr_dots = thinking_label.text.count(".")

            if curr_dots >= 3:
                thinking_label.text = base_text + "."
            else:
                thinking_label.text = base_text + "." * (curr_dots + 1)

        anim_event = Clock.schedule_interval(
            shift_dots,
            0.5
        )

        # Background generation thread
        def generate_summary():

            try:

                # SAFE TOKENIZATION
                inputs = tokenizer(
                    original_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=1024
                )

                summary_ids = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],

                    max_length=180,
                    min_length=40,

                    num_beams=4,

                    repetition_penalty=1.2,
                    length_penalty=2.0,

                    no_repeat_ngram_size=3,

                    early_stopping=True,
                    do_sample=False
                )

                final_text = tokenizer.decode(
                    summary_ids[0],
                    skip_special_tokens=True
                )

                # Clean spacing
                final_text = re.sub(
                    r"\s+",
                    " ",
                    final_text
                ).strip()

            except Exception as e:

                final_text = f"Error: {str(e)}"

            Clock.schedule_once(
                lambda dt: update_ui(final_text),
                0
            )

        def update_ui(final_text):

            anim_event.cancel()

            if thinking_label:

                thinking_label.text = final_text
                thinking_label.texture_update()

        threading.Thread(
            target=generate_summary,
            daemon=True
        ).start()

    # -----------------------------------------------------
    # CHAT BUBBLE
    # -----------------------------------------------------

    def chat_bubble(
        self,
        text,
        sender,
        chat_list,
        scroll_view,
        original_prompt=""
    ):

        app = MDApp.get_running_app()

        is_user = sender == "user"

        bg_color = (
            (0, 0, 0, 1)
            if is_user
            else
            (0.9, 0.9, 0.9, 1)
        )

        font_color = (
            (1, 1, 1, 1)
            if is_user
            else
            (0, 0, 0, 1)
        )

        user_initial = (
            getattr(app, 'user_name', "U")[0].upper()
            if getattr(app, 'user_name', None)
            else "U"
        )

        avatar_letter = (
            user_initial
            if is_user
            else "Re"
        )

        row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            adaptive_height=True,
            spacing="10dp",
            padding="5dp",
            opacity=0
        )

        avatar = MDCard(
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            radius=[dp(20)] * 4,
            md_bg_color=bg_color,
            pos_hint={"top": 1}
        )

        avatar.add_widget(
            MDLabel(
                text=avatar_letter,
                halign="center",
                theme_text_color="Custom",
                text_color=font_color
            )
        )

        bubble_wrapper = MDBoxLayout(
            orientation="vertical",
            size_hint_x=0.7,
            adaptive_height=True
        )

        bubble = MDCard(
            orientation="vertical",
            size_hint_x=1,
            adaptive_height=True,
            md_bg_color=bg_color,
            padding="12dp",
            radius=[dp(15)] * 4
        )

        lbl = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=font_color,
            adaptive_height=True,
        )

        lbl.bind(
            on_touch_down=lambda instance, touch:
            self.on_label_click(instance, touch)
        )

        bubble.add_widget(lbl)
        bubble_wrapper.add_widget(bubble)

        spacer = Widget(size_hint_x=0.2)

        if is_user:

            row.add_widget(spacer)
            row.add_widget(bubble_wrapper)
            row.add_widget(avatar)

        else:

            feedback_btn = MDIconButton(
                icon="comment",
                icon_size="20sp",
                pos_hint={"center_y": 0.5},
                on_release=lambda x:
                self.show_feedback_dialog(
                    original_prompt,
                    lbl.text
                )
            )

            row.add_widget(avatar)
            row.add_widget(bubble_wrapper)
            row.add_widget(feedback_btn)
            row.add_widget(spacer)

        chat_list.add_widget(row)

        Clock.schedule_once(
            lambda dt:
            setattr(scroll_view, 'scroll_y', 0),
            0.1
        )

        Animation(
            opacity=1,
            duration=0.3
        ).start(row)

        return lbl

    # -----------------------------------------------------
    # FEEDBACK DIALOG
    # -----------------------------------------------------

    def show_feedback_dialog(
        self,
        prompt_text,
        bot_response
    ):

        self.feedback_content = FeedbackContent()

        self.submit_btn = MDFlatButton(
            text="SUBMIT",
            disabled=True,
            theme_text_color="Hint",
            on_release=lambda x:
            self.submit_feedback(
                prompt_text,
                bot_response
            )
        )

        self.dialog = MDDialog(
            title="Rate this response",
            type="custom",
            content_cls=self.feedback_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x:
                    self.dialog.dismiss()
                ),
                self.submit_btn
            ]
        )

        self.feedback_content.consent_checkbox.bind(
            active=self.toggle_submit_button
        )

        self.dialog.open()

    # -----------------------------------------------------
    # TOGGLE SUBMIT
    # -----------------------------------------------------

    def toggle_submit_button(
        self,
        checkbox_instance,
        is_active
    ):

        self.submit_btn.disabled = not is_active

        self.submit_btn.theme_text_color = (
            "Primary"
            if is_active
            else "Hint"
        )

    # -----------------------------------------------------
    # SUBMIT FEEDBACK
    # -----------------------------------------------------

    def submit_feedback(
        self,
        prompt_text,
        bot_response
    ):

        app = MDApp.get_running_app()

        ratings_dict = self.feedback_content.ratings
        feedback_text = self.feedback_content.feedback_input.text

        user_uuid = getattr(
            app,
            'user_uuid',
            "Unknown_UUID"
        )

        self.dialog.dismiss()

        threading.Thread(
            target=self._upload_to_sheets_worker,
            args=(
                prompt_text,
                bot_response,
                ratings_dict,
                feedback_text,
                user_uuid
            ),
            daemon=True
        ).start()

    # -----------------------------------------------------
    # GOOGLE SHEETS WORKER
    # -----------------------------------------------------

    def _upload_to_sheets_worker(
        self,
        prompt_text,
        bot_response,
        ratings_dict,
        feedback_text,
        user_uuid
    ):

        try:

            gc = gspread.service_account(
                filename="credentials.json"
            )

            sheet = gc.open_by_key(
                "1nmiDOoYGxnxlJ5v0fxGJqF0i2LzaVJSHKzcTEIAoawQ"
            ).sheet1

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

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

            sheet.append_row(row_data)

            print("Feedback uploaded successfully!")

        except Exception as e:

            print(f"Google Sheets upload failed: {e}")