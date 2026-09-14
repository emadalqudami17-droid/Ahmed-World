# -*- coding: utf-8 -*-

import os
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import (
    Color,
    RoundedRectangle,
    Rectangle,
    Ellipse,
    Line,
    Triangle,
)
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


# ============================================================
# FONT REGISTRATION (MUST BE BEFORE ANY Label)
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_font():
    """Try to locate the Arabic font in several possible locations."""
    candidates = [
        os.path.join(BASE_DIR, "NotoNaskhArabic-Regular.ttf"),
        "NotoNaskhArabic-Regular.ttf",
        os.path.join(os.getcwd(), "NotoNaskhArabic-Regular.ttf"),
    ]
    try:
        app = App.get_running_app()
        if app:
            candidates.insert(
                0,
                os.path.join(app.directory, "NotoNaskhArabic-Regular.ttf"),
            )
    except Exception:
        pass

    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


_FONT_PATH = _find_font()

try:
    LabelBase.register(name="Arabic", fn_regular=_FONT_PATH)
except Exception:
    # If font file is missing, Kivy falls back to default (will show boxes)
    pass


# ============================================================
# ARABIC TEXT SHAPING
# ============================================================

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar(text):
        """Prepare Arabic text for correct Kivy display."""
        return get_display(arabic_reshaper.reshape(text))

except Exception:

    def ar(text):
        return text


# ============================================================
# PATHS
# ============================================================

def asset(path):
    """Find asset in several possible locations (Android-friendly)."""
    candidates = [
        os.path.join(BASE_DIR, path),
        path,
        os.path.join(os.getcwd(), path),
    ]
    try:
        app = App.get_running_app()
        if app:
            candidates.insert(0, os.path.join(app.directory, path))
    except Exception:
        pass

    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


def image_path(filename):
    return asset(os.path.join("images", filename))


def audio_path(filename):
    return asset(os.path.join("audio", filename))


# ============================================================
# COLORS / THEME
# ============================================================

BG_COLOR = (0.965, 0.975, 0.995, 1)
NAVY = (0.10, 0.22, 0.38, 1)
BLUE = (0.20, 0.48, 0.78, 1)
LIGHT_BLUE = (0.88, 0.94, 0.99, 1)
GOLD = (0.93, 0.70, 0.18, 1)
GREEN = (0.25, 0.67, 0.43, 1)
RED = (0.86, 0.30, 0.30, 1)
WHITE = (1, 1, 1, 1)
TEXT = (0.12, 0.17, 0.25, 1)
MUTED = (0.40, 0.46, 0.55, 1)

CARD_COLORS = [
    (0.89, 0.95, 1.00, 1),
    (0.96, 0.91, 0.99, 1),
    (0.91, 0.98, 0.93, 1),
    (1.00, 0.95, 0.87, 1),
    (0.91, 0.96, 1.00, 1),
    (0.98, 0.92, 0.94, 1),
    (0.92, 0.98, 0.97, 1),
    (1.00, 0.96, 0.88, 1),
]


# ============================================================
# BASIC HELPERS
# ============================================================

def make_label(text="", size=20, color=TEXT, **kwargs):
    label = Label(
        text=ar(text),
        font_size=dp(size),
        color=color,
        font_name="Arabic",
        halign="center",
        valign="middle",
        **kwargs
    )
    label.bind(size=lambda obj, value: setattr(obj, "text_size", value))
    return label


# ============================================================
# ROUNDED BUTTON
# ============================================================

class RoundButton(ButtonBehavior, Label):

    def __init__(
        self,
        text="",
        button_color=BLUE,
        text_color=WHITE,
        height=52,
        **kwargs
    ):
        super().__init__(
            text=ar(text),
            color=text_color,
            font_size=dp(18),
            font_name="Arabic",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(height),
            **kwargs
        )

        self.button_color = button_color
        self.normal_color = button_color
        self.pressed_color = tuple(max(0, x * 0.82) for x in button_color)

        with self.canvas.before:
            self.bg_color = Color(*self.normal_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(18)]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_press(self):
        self.bg_color.rgba = self.pressed_color

    def on_release(self):
        self.bg_color.rgba = self.normal_color


# ============================================================
# ROUNDED CARD
# ============================================================

class RoundedCard(ButtonBehavior, BoxLayout):

    def __init__(
        self,
        card_color=(1, 1, 1, 1),
        orientation="vertical",
        padding=10,
        spacing=5,
        **kwargs
    ):
        super().__init__(
            orientation=orientation,
            padding=dp(padding),
            spacing=dp(spacing),
            **kwargs
        )

        self.card_color = card_color

        with self.canvas.before:
            self.shadow_color = Color(0, 0, 0, 0.08)
            self.shadow_rect = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[dp(20)]
            )

            self.bg_color = Color(*card_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )

        self.bind(
            pos=self.update_card,
            size=self.update_card
        )

    def update_card(self, *args):
        self.shadow_rect.pos = (
            self.x + dp(2),
            self.y - dp(2)
        )
        self.shadow_rect.size = self.size

        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_press(self):
        self.bg_color.rgba = tuple(
            max(0, x * 0.92) for x in self.card_color
        )

    def on_release(self):
        self.bg_color.rgba = self.card_color


# ============================================================
# SHAPE DRAWING WIDGET
# ============================================================

class ShapeWidget(Widget):

    def __init__(
        self,
        shape="circle",
        shape_color=BLUE,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.shape = shape
        self.shape_color = shape_color

        with self.canvas:
            self.color_instruction = Color(*shape_color)

            self.shape_ellipse = Ellipse()
            self.shape_rectangle = Rectangle()
            self.shape_triangle = Triangle()

            self.shape_line = Line(
                width=dp(5),
                close=True
            )

        self.bind(
            pos=self.draw_shape,
            size=self.draw_shape
        )

        Clock.schedule_once(self.draw_shape, 0)

    def draw_shape(self, *args):
        x, y = self.x, self.y
        w, h = self.width, self.height

        size = min(w, h) * 0.62
        if size <= 0:
            return

        cx = x + w / 2
        cy = y + h / 2
        left = cx - size / 2
        bottom = cy - size / 2

        # Safe reset
        self.shape_ellipse.size = (size, size)
        self.shape_ellipse.pos = (left, bottom)
        self.shape_rectangle.size = (size, size)
        self.shape_rectangle.pos = (left, bottom)
        self.shape_triangle.points = [
            cx, cy + size / 2,
            cx - size / 2, cy - size / 2,
            cx + size / 2, cy - size / 2,
        ]

        # Hide all first
        self.shape_ellipse.opacity = 0
        self.shape_rectangle.opacity = 0
        self.shape_triangle.opacity = 0
        self.shape_line.points = []

        if self.shape == "circle":
            self.shape_ellipse.opacity = 1

        elif self.shape == "square":
            self.shape_rectangle.opacity = 1

        elif self.shape == "triangle":
            self.shape_triangle.opacity = 1

        elif self.shape == "rectangle":
            self.shape_rectangle.opacity = 1
            rect_w = size * 1.25
            rect_h = size * 0.72
            self.shape_rectangle.size = (rect_w, rect_h)
            self.shape_rectangle.pos = (
                cx - rect_w / 2,
                cy - rect_h / 2,
            )

        elif self.shape == "star":
            import math
            points = []
            for i in range(10):
                angle = math.radians(90 + i * 36)
                radius = size / 2 if i % 2 == 0 else size / 4
                points.extend([
                    cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle),
                ])
            if len(points) >= 4:
                self.shape_line.points = points

        elif self.shape == "heart":
            points = [
                cx, cy - size * 0.42,
                cx - size * 0.45, cy - size * 0.02,
                cx - size * 0.40, cy + size * 0.28,
                cx, cy + size * 0.48,
                cx + size * 0.40, cy + size * 0.28,
                cx + size * 0.45, cy - size * 0.02,
                cx, cy - size * 0.42,
            ]
            if len(points) >= 4:
                self.shape_line.points = points


# ============================================================
# BASE SCREEN
# ============================================================

class BaseScreen(Screen):

    def on_pre_enter(self, *args):
        Window.clearcolor = BG_COLOR

    def build_header(self, title, show_back=True):

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(65),
            spacing=dp(8),
            padding=(dp(8), dp(8))
        )

        if show_back:

            back = RoundButton(
                text="رجوع",
                button_color=NAVY,
                height=49
            )

            back.size_hint_x = None
            back.width = dp(90)

            back.bind(
                on_release=lambda *_:
                self.go_main()
            )

            header.add_widget(back)

        else:

            spacer = Widget(
                size_hint_x=None,
                width=dp(90)
            )

            header.add_widget(spacer)

        title_label = make_label(
            title,
            size=23,
            color=NAVY
        )

        header.add_widget(title_label)

        stars = make_label(
            "★ 0",
            size=18,
            color=GOLD
        )

        stars.size_hint_x = None
        stars.width = dp(75)

        header.add_widget(stars)

        self.star_header = stars

        return header

    def refresh_stars(self):
        if hasattr(self, "star_header"):
            app = App.get_running_app()
            self.star_header.text = f"★ {app.stars}"

    def go_main(self):
        manager = self.manager

        if manager:
            manager.transition = SlideTransition(
                direction="right"
            )
            manager.current = "main_menu"


# ============================================================
# SPLASH SCREEN
# ============================================================

class SplashScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(35),
            spacing=dp(15)
        )

        layout.add_widget(
            Widget(size_hint_y=0.15)
        )

        icon = Image(
            source=asset("app_icon.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.42
        )

        layout.add_widget(icon)

        title = make_label(
            "عالم أحمد",
            size=34,
            color=NAVY,
            size_hint_y=None,
            height=dp(65)
        )

        layout.add_widget(title)

        greeting = make_label(
            "أهلاً أحمد!",
            size=25,
            color=GOLD,
            size_hint_y=None,
            height=dp(55)
        )

        layout.add_widget(greeting)

        subtitle = make_label(
            "هيا نتعلم ونلعب معًا",
            size=19,
            color=MUTED,
            size_hint_y=None,
            height=dp(50)
        )

        layout.add_widget(subtitle)

        layout.add_widget(
            Widget(size_hint_y=0.20)
        )

        self.add_widget(layout)

    def on_enter(self, *args):

        Clock.schedule_once(
            self.open_main,
            3.0
        )

    def open_main(self, dt):

        if self.manager:
            self.manager.current = "main_menu"


# ============================================================
# MAIN MENU
# ============================================================

class MainMenuScreen(BaseScreen):

    sections = [
        ("★", "التركيز والانتباه", "focus"),
        ("♥", "عائلتي", "family"),
        ("▲", "الأشكال", "shapes"),
        ("■", "الحمام", "toilet"),
        ("●", "الوضوء", "wudu"),
        ("◆", "أريد / التواصل", "communication"),
        ("✓", "النظافة", "hygiene"),
        ("★", "المكافآت والتقدم", "rewards"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.root_layout.clear_widgets()

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=(dp(8), dp(5))
        )

        profile_image = Image(
            source=image_path("family_ahmed.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=None,
            width=dp(70)
        )

        header.add_widget(profile_image)

        title_box = BoxLayout(
            orientation="vertical"
        )

        title_box.add_widget(
            make_label(
                "عالم أحمد",
                size=27,
                color=NAVY
            )
        )

        title_box.add_widget(
            make_label(
                "أهلاً أحمد! هيا نتعلم",
                size=17,
                color=MUTED
            )
        )

        header.add_widget(title_box)

        app = App.get_running_app()

        stars = make_label(
            f"★ {app.stars}",
            size=20,
            color=GOLD
        )

        stars.size_hint_x = None
        stars.width = dp(80)

        header.add_widget(stars)

        self.root_layout.add_widget(header)

        # ----------------------------------------------------
        # Scroll area
        # ----------------------------------------------------

        scroll = ScrollView(
            do_scroll_x=False
        )

        grid = GridLayout(
            cols=2,
            spacing=dp(12),
            padding=dp(8),
            size_hint_y=None
        )

        grid.bind(
            minimum_height=grid.setter("height")
        )

        for index, (icon, title, screen_name) in enumerate(
            self.sections
        ):

            completed = screen_name in app.completed

            card = RoundedCard(
                card_color=CARD_COLORS[
                    index % len(CARD_COLORS)
                ],
                size_hint_y=None,
                height=dp(155)
            )

            icon_label = make_label(
                icon,
                size=45,
                color=NAVY,
                size_hint_y=None,
                height=dp(55)
            )

            card.add_widget(icon_label)

            title_label = make_label(
                title,
                size=19,
                color=TEXT
            )

            card.add_widget(title_label)

            status = (
                "★ مكتمل"
                if completed
                else "اضغط للبدء"
            )

            status_label = make_label(
                status,
                size=14,
                color=GOLD if completed else MUTED,
                size_hint_y=None,
                height=dp(28)
            )

            card.add_widget(status_label)

            card.bind(
                on_release=lambda instance,
                name=screen_name:
                self.open_section(name)
            )

            grid.add_widget(card)

        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        footer = make_label(
            "اختر نشاطًا لنبدأ!",
            size=17,
            color=MUTED,
            size_hint_y=None,
            height=dp(42)
        )

        self.root_layout.add_widget(footer)

    def open_section(self, name):

        if self.manager:
            self.manager.transition = SlideTransition(
                direction="left"
            )
            self.manager.current = name


# ============================================================
# GENERIC STEP LEARNING SCREEN
# ============================================================

class StepScreen(BaseScreen):

    section_id = ""
    title = ""
    steps = []
    complete_audio = "reward_complete.wav"
    complete_message = "أحسنت! أكملت النشاط."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_step = 0
        self.finished = False

        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        self.add_widget(self.main_layout)

    def on_pre_enter(self, *args):

        super().on_pre_enter(*args)

        self.current_step = 0
        self.finished = False

        self.build_ui()

        Clock.schedule_once(
            lambda dt: self.play_current_audio(),
            0.4
        )

    def build_ui(self):

        self.main_layout.clear_widgets()

        self.main_layout.add_widget(
            self.build_header(self.title)
        )

        progress = make_label(
            "",
            size=17,
            color=BLUE,
            size_hint_y=None,
            height=dp(35)
        )

        self.progress_label = progress

        self.main_layout.add_widget(progress)

        image = Image(
            source="",
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.55
        )

        self.step_image = image

        self.main_layout.add_widget(image)

        caption = make_label(
            "",
            size=24,
            color=NAVY,
            size_hint_y=None,
            height=dp(65)
        )

        self.caption_label = caption

        self.main_layout.add_widget(caption)

        play_button = RoundButton(
            text="🔊 استمع مرة أخرى",
            button_color=BLUE,
            height=52
        )

        play_button.bind(
            on_release=lambda *_:
            self.play_current_audio()
        )

        self.main_layout.add_widget(play_button)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(10)
        )

        previous = RoundButton(
            text="السابق",
            button_color=MUTED,
            height=52
        )

        previous.bind(
            on_release=lambda *_:
            self.previous_step()
        )

        next_button = RoundButton(
            text="التالي",
            button_color=GREEN,
            height=52
        )

        next_button.bind(
            on_release=lambda *_:
            self.next_step()
        )

        self.previous_button = previous
        self.next_button = next_button

        buttons.add_widget(previous)
        buttons.add_widget(next_button)

        self.main_layout.add_widget(buttons)

        self.update_step()

    def update_step(self):

        if not self.steps:
            return

        step = self.steps[self.current_step]

        self.step_image.source = image_path(
            step["image"]
        )

        self.caption_label.text = ar(
            step["text"]
        )

        total = len(self.steps)

        self.progress_label.text = ar(
            f"الخطوة {self.current_step + 1} من {total}"
        )

        self.previous_button.disabled = (
            self.current_step == 0
        )

        if self.current_step == total - 1:
            self.next_button.text = ar("أكملت")
        else:
            self.next_button.text = ar("التالي")

        self.refresh_stars()

    def play_current_audio(self):

        if self.finished:
            return

        step = self.steps[self.current_step]

        App.get_running_app().play_audio(
            step["audio"]
        )

    def previous_step(self):

        if self.current_step > 0:

            self.current_step -= 1

            self.update_step()
            self.play_current_audio()

    def next_step(self):

        if self.finished:
            self.current_step = 0
            self.finished = False
            self.update_step()
            self.play_current_audio()
            return

        if self.current_step < len(self.steps) - 1:

            App.get_running_app().play_audio(
                "cheer.wav"
            )

            self.current_step += 1

            Clock.schedule_once(
                lambda dt: self.update_and_play(),
                0.7
            )

        else:

            self.finish_activity()

    def update_and_play(self):

        self.update_step()
        self.play_current_audio()

    def finish_activity(self):

        self.finished = True

        app = App.get_running_app()

        app.award_star(
            self.section_id
        )

        App.get_running_app().play_audio(
            self.complete_audio
        )

        self.caption_label.text = ar(
            self.complete_message
        )

        self.next_button.text = ar(
            "ابدأ من جديد"
        )

        self.progress_label.text = ar(
            "أحسنت! النشاط مكتمل ★"
        )


# ============================================================
# BATHROOM
# ============================================================

class ToiletScreen(StepScreen):

    section_id = "toilet"
    title = "الحمام"

    complete_message = (
        "أحسنت يا أحمد! أكملت خطوات الحمام."
    )

    steps = [
        {
            "image": "step1_feel.png",
            "audio": "audio1.wav",
            "text": "أشعر أنني أريد الذهاب إلى الحمام."
        },
        {
            "image": "step2_walk.png",
            "audio": "audio2.wav",
            "text": "أذهب إلى الحمام."
        },
        {
            "image": "step3_pants_down.png",
            "audio": "audio3.wav",
            "text": "أنزل ملابسي."
        },
        {
            "image": "step4_sit.png",
            "audio": "audio4.wav",
            "text": "أجلس على المرحاض."
        },
        {
            "image": "step5_clean.png",
            "audio": "audio5.wav",
            "text": "أنظف نفسي."
        },
        {
            "image": "step6_pants_up.png",
            "audio": "audio6.wav",
            "text": "أرفع ملابسي."
        },
        {
            "image": "step7_wash_hands.png",
            "audio": "audio7.wav",
            "text": "أغسل يدي."
        },
    ]


# ============================================================
# WUDU
# ============================================================

class WuduScreen(StepScreen):

    section_id = "wudu"
    title = "الوضوء"

    complete_audio = "wudu_complete.wav"

    complete_message = (
        "أحسنت يا أحمد! أكملت الوضوء."
    )

    steps = [
        {
            "image": "wudu_01_hands.png",
            "audio": "wudu_01_hands.wav",
            "text": "أغسل يدي."
        },
        {
            "image": "wudu_02_mouth.png",
            "audio": "wudu_02_mouth.wav",
            "text": "أغسل فمي."
        },
        {
            "image": "wudu_03_nose.png",
            "audio": "wudu_03_nose.wav",
            "text": "أغسل أنفي."
        },
        {
            "image": "wudu_04_face.png",
            "audio": "wudu_04_face.wav",
            "text": "أغسل وجهي."
        },
        {
            "image": "wudu_05_right_arm.png",
            "audio": "wudu_05_arm.wav",
            "text": "أغسل ذراعي."
        },
        {
            "image": "wudu_06_head.png",
            "audio": "wudu_06_head.wav",
            "text": "أمسح رأسي."
        },
        {
            "image": "wudu_07_ears.png",
            "audio": "wudu_07_ears.wav",
            "text": "أمسح أذني."
        },
        {
            "image": "wudu_08_feet.png",
            "audio": "wudu_08_feet.wav",
            "text": "أغسل قدمي."
        },
    ]


# ============================================================
# HYGIENE
# ============================================================

class HygieneScreen(StepScreen):

    section_id = "hygiene"
    title = "النظافة"

    complete_message = (
        "أحسنت يا أحمد! تعلمت خطوات النظافة."
    )

    steps = [
        {
            "image": "hygiene_brush_teeth.png",
            "audio": "hygiene_brush_teeth.wav",
            "text": "أنظف أسناني."
        },
        {
            "image": "hygiene_bath.png",
            "audio": "hygiene_bath.wav",
            "text": "أستحم وأنظف جسمي."
        },
        {
            "image": "hygiene_soap.png",
            "audio": "hygiene_soap.wav",
            "text": "أستخدم الصابون."
        },
        {
            "image": "hygiene_towel.png",
            "audio": "hygiene_towel.wav",
            "text": "أجفف يدي بالمنشفة."
        },
        {
            "image": "hygiene_wash_hands.png",
            "audio": "hygiene_wash_hands.wav",
            "text": "أغسل يدي بالماء والصابون."
        },
    ]


# ============================================================
# FAMILY
# ============================================================

class FamilyScreen(BaseScreen):

    people = [
        (
            "family_ahmed.png",
            "أحمد",
            "say_ahmed.wav"
        ),
        (
            "family_dad.png",
            "أبي",
            "say_dad.wav"
        ),
        (
            "family_mohamed.png",
            "محمد",
            "say_mohamed.wav"
        ),
        (
            "family_milad.png",
            "ميلاد",
            "say_milad.wav"
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tapped = set()

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.tapped = set()

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            self.build_header("عائلتي")
        )

        intro = make_label(
            "تعرف على أفراد عائلتك",
            size=20,
            color=NAVY,
            size_hint_y=None,
            height=dp(45)
        )

        self.root_layout.add_widget(intro)

        grid = GridLayout(
            cols=2,
            spacing=dp(12),
            padding=dp(8),
            size_hint_y=None
        )

        grid.bind(
            minimum_height=grid.setter("height")
        )

        for index, (
            filename,
            name,
            audio
        ) in enumerate(self.people):

            card = RoundedCard(
                card_color=CARD_COLORS[
                    index % len(CARD_COLORS)
                ],
                size_hint_y=None,
                height=dp(205)
            )

            photo = Image(
                source=image_path(filename),
                allow_stretch=True,
                keep_ratio=True
            )

            card.add_widget(photo)

            label = make_label(
                name,
                size=21,
                color=NAVY,
                size_hint_y=None,
                height=dp(40)
            )

            card.add_widget(label)

            card.bind(
                on_release=lambda instance,
                i=index,
                snd=audio:
                self.person_selected(i, snd)
            )

            grid.add_widget(card)

        scroll = ScrollView(
            do_scroll_x=False
        )

        scroll.add_widget(grid)

        self.root_layout.add_widget(scroll)

        self.status = make_label(
            "اضغط على صورة لسماع الاسم",
            size=16,
            color=MUTED,
            size_hint_y=None,
            height=dp(40)
        )

        self.root_layout.add_widget(self.status)

        self.refresh_stars()

    def person_selected(self, index, audio):

        self.tapped.add(index)

        App.get_running_app().play_audio(
            audio
        )

        if len(self.tapped) == len(self.people):

            self.status.text = ar(
                "أحسنت! تعرفت على عائلتك ★"
            )

            App.get_running_app().award_star(
                "family"
            )


# ============================================================
# COMMUNICATION / AAC
# ============================================================

class CommunicationScreen(BaseScreen):

    cards = [
        (
            "family_ahmed.png",
            "أحمد",
            "say_ahmed.wav"
        ),
        (
            "family_dad.png",
            "أبي",
            "say_dad.wav"
        ),
        (
            "family_mohamed.png",
            "محمد",
            "say_mohamed.wav"
        ),
        (
            "family_milad.png",
            "ميلاد",
            "say_milad.wav"
        ),
        (
            "aac_water.png",
            "ماء",
            "say_water.wav"
        ),
        (
            "aac_food.png",
            "طعام",
            "say_food.wav"
        ),
        (
            "aac_toilet.png",
            "حمام",
            "say_toilet.wav"
        ),
        (
            "aac_sleep.png",
            "نوم",
            "say_sleep.wav"
        ),
        (
            "aac_help.png",
            "ساعدني",
            "say_help.wav"
        ),
        (
            "aac_play.png",
            "أريد أن ألعب",
            "say_play.wav"
        ),
        (
            "aac_stop.png",
            "توقف",
            "say_stop.wav"
        ),
        (
            "aac_happy.png",
            "أنا سعيد",
            "say_happy.wav"
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.used = set()

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.used = set()

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            self.build_header("أريد / التواصل")
        )

        intro = make_label(
            "اضغط على الصورة لتقول ما تريد",
            size=19,
            color=NAVY,
            size_hint_y=None,
            height=dp(42)
        )

        self.root_layout.add_widget(intro)

        scroll = ScrollView(
            do_scroll_x=False
        )

        grid = GridLayout(
            cols=3,
            spacing=dp(10),
            padding=dp(6),
            size_hint_y=None
        )

        grid.bind(
            minimum_height=grid.setter("height")
        )

        for index, (
            filename,
            text,
            audio
        ) in enumerate(self.cards):

            card = RoundedCard(
                card_color=CARD_COLORS[
                    index % len(CARD_COLORS)
                ],
                size_hint_y=None,
                height=dp(170)
            )

            image = Image(
                source=image_path(filename),
                allow_stretch=True,
                keep_ratio=True
            )

            card.add_widget(image)

            label = make_label(
                text,
                size=16,
                color=TEXT,
                size_hint_y=None,
                height=dp(42)
            )

            card.add_widget(label)

            card.bind(
                on_release=lambda instance,
                i=index,
                snd=audio:
                self.communication_selected(i, snd)
            )

            grid.add_widget(card)

        scroll.add_widget(grid)

        self.root_layout.add_widget(scroll)

        self.status = make_label(
            "0 / 12",
            size=16,
            color=MUTED,
            size_hint_y=None,
            height=dp(38)
        )

        self.root_layout.add_widget(self.status)

        self.refresh_stars()

    def communication_selected(
        self,
        index,
        audio
    ):

        self.used.add(index)

        App.get_running_app().play_audio(
            audio
        )

        self.status.text = ar(
            f"{len(self.used)} / {len(self.cards)}"
        )

        if len(self.used) == len(self.cards):

            self.status.text = ar(
                "أحسنت! تعلمت كلمات التواصل ★"
            )

            App.get_running_app().award_star(
                "communication"
            )


# ============================================================
# FOCUS / ATTENTION
# ============================================================

class FocusScreen(BaseScreen):

    targets = [
        {
            "id": "ahmed",
            "image": "family_ahmed.png",
            "symbol": "",
            "audio": "focus_find_ahmed.wav",
            "name": "أحمد"
        },
        {
            "id": "dad",
            "image": "family_dad.png",
            "symbol": "",
            "audio": "focus_find_dad.wav",
            "name": "أبي"
        },
        {
            "id": "mohamed",
            "image": "family_mohamed.png",
            "symbol": "",
            "audio": "focus_find_mohamed.wav",
            "name": "محمد"
        },
        {
            "id": "milad",
            "image": "family_milad.png",
            "symbol": "",
            "audio": "focus_find_milad.wav",
            "name": "ميلاد"
        },
        {
            "id": "apple",
            "image": None,
            "symbol": "★",
            "audio": "focus_find_apple.wav",
            "name": "التفاحة"
        },
        {
            "id": "car",
            "image": None,
            "symbol": "▲",
            "audio": "focus_find_car.wav",
            "name": "السيارة"
        },
        {
            "id": "cat",
            "image": None,
            "symbol": "●",
            "audio": "focus_find_cat.wav",
            "name": "القطة"
        },
        {
            "id": "dog",
            "image": None,
            "symbol": "■",
            "audio": "focus_find_dog.wav",
            "name": "الكلب"
        },
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.score = 0
        self.rounds = 0
        self.current_target = None
        self.options = []

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.score = 0
        self.rounds = 0

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            self.build_header(
                "التركيز والانتباه"
            )
        )

        instruction = make_label(
            "انظر جيدًا واختر الصحيح",
            size=20,
            color=NAVY,
            size_hint_y=None,
            height=dp(42)
        )

        self.root_layout.add_widget(
            instruction
        )

        self.question = make_label(
            "استمع...",
            size=25,
            color=BLUE,
            size_hint_y=None,
            height=dp(55)
        )

        self.root_layout.add_widget(
            self.question
        )

        self.options_grid = GridLayout(
            cols=3,
            spacing=dp(10),
            padding=dp(6),
            size_hint_y=0.65
        )

        self.root_layout.add_widget(
            self.options_grid
        )

        self.score_label = make_label(
            "0 / 5",
            size=17,
            color=MUTED,
            size_hint_y=None,
            height=dp(35)
        )

        self.root_layout.add_widget(
            self.score_label
        )

        self.new_round()

    def new_round(self):

        self.current_target = random.choice(
            self.targets
        )

        others = [
            item for item in self.targets
            if item["id"] != self.current_target["id"]
        ]

        self.options = random.sample(
            others,
            2
        ) + [self.current_target]

        random.shuffle(self.options)

        self.options_grid.clear_widgets()

        for item in self.options:

            card = RoundedCard(
                card_color=LIGHT_BLUE,
                size_hint_y=None,
                height=dp(180)
            )

            if item["image"]:

                image = Image(
                    source=image_path(
                        item["image"]
                    ),
                    allow_stretch=True,
                    keep_ratio=True
                )

                card.add_widget(image)

            else:

                symbol = make_label(
                    item["symbol"],
                    size=52,
                    color=NAVY
                )

                card.add_widget(symbol)

            name_label = make_label(
                item["name"],
                size=14,
                color=MUTED,
                size_hint_y=None,
                height=dp(32)
            )

            card.add_widget(name_label)

            card.bind(
                on_release=lambda instance,
                selected=item:
                self.check_answer(selected)
            )

            self.options_grid.add_widget(card)

        Clock.schedule_once(
            lambda dt: self.ask_question(),
            0.3
        )

    def ask_question(self):

        App.get_running_app().play_audio(
            "focus_look.wav"
        )

        Clock.schedule_once(
            lambda dt:
            App.get_running_app().play_audio(
                self.current_target["audio"]
            ),
            0.8
        )

        self.question.text = ar(
            "أين هو؟"
        )

    def check_answer(self, selected):

        if self.current_target is None:
            return

        if selected["id"] == self.current_target["id"]:

            self.score += 1
            self.rounds += 1

            App.get_running_app().play_audio(
                "cheer.wav"
            )

            self.score_label.text = ar(
                f"{self.score} / 5"
            )

            if self.score >= 5:

                App.get_running_app().award_star(
                    "focus"
                )

                Clock.schedule_once(
                    lambda dt:
                    self.finish_focus(),
                    0.7
                )

            else:

                Clock.schedule_once(
                    lambda dt:
                    self.new_round(),
                    0.8
                )

        else:

            App.get_running_app().play_audio(
                "focus_try_again.wav"
            )

    def finish_focus(self):

        App.get_running_app().play_audio(
            "reward_complete.wav"
        )

        self.question.text = ar(
            "أحسنت يا أحمد! ممتاز!"
        )

        self.score_label.text = ar(
            "النشاط مكتمل ★"
        )


# ============================================================
# SHAPES
# ============================================================

class ShapesScreen(BaseScreen):

    shapes = [
        (
            "circle",
            "دائرة",
            "shape_circle.wav"
        ),
        (
            "square",
            "مربع",
            "shape_square.wav"
        ),
        (
            "triangle",
            "مثلث",
            "shape_triangle.wav"
        ),
        (
            "rectangle",
            "مستطيل",
            "shape_rectangle.wav"
        ),
        (
            "star",
            "نجمة",
            "shape_star.wav"
        ),
        (
            "heart",
            "قلب",
            "shape_heart.wav"
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.correct = 0
        self.target = None

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.correct = 0

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            self.build_header("الأشكال")
        )

        self.target_area = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(170)
        )

        self.target_shape = ShapeWidget(
            shape="circle",
            shape_color=BLUE
        )

        self.target_area.add_widget(
            self.target_shape
        )

        self.root_layout.add_widget(
            self.target_area
        )

        self.question = make_label(
            "اختر الشكل الصحيح",
            size=21,
            color=NAVY,
            size_hint_y=None,
            height=dp(42)
        )

        self.root_layout.add_widget(
            self.question
        )

        self.grid = GridLayout(
            cols=3,
            spacing=dp(10),
            padding=dp(6)
        )

        self.root_layout.add_widget(
            self.grid
        )

        self.score_label = make_label(
            "0 / 5",
            size=17,
            color=MUTED,
            size_hint_y=None,
            height=dp(35)
        )

        self.root_layout.add_widget(
            self.score_label
        )

        self.new_question()

    def new_question(self):

        self.target = random.choice(
            self.shapes
        )

        shape_name = self.target[0]

        self.target_shape.shape = shape_name
        self.target_shape.shape_color = BLUE

        # Refresh drawing
        self.target_shape.draw_shape()

        self.grid.clear_widgets()

        options = list(self.shapes)

        random.shuffle(options)

        for shape_type, name, audio in options:

            card = RoundedCard(
                card_color=WHITE,
                size_hint_y=None,
                height=dp(145)
            )

            shape = ShapeWidget(
                shape=shape_type,
                shape_color=GOLD
            )

            card.add_widget(shape)

            label = make_label(
                name,
                size=15,
                color=TEXT,
                size_hint_y=None,
                height=dp(30)
            )

            card.add_widget(label)

            card.bind(
                on_release=lambda instance,
                st=shape_type,
                snd=audio:
                self.check_shape(
                    st,
                    snd
                )
            )

            self.grid.add_widget(card)

        App.get_running_app().play_audio(
            "find_shape.wav"
        )

    def check_shape(
        self,
        selected_shape,
        audio
    ):

        if self.target is None:
            return

        App.get_running_app().play_audio(
            audio
        )

        if selected_shape == self.target[0]:

            self.correct += 1

            Clock.schedule_once(
                lambda dt:
                App.get_running_app().play_audio(
                    "cheer.wav"
                ),
                0.5
            )

            self.score_label.text = ar(
                f"{self.correct} / 5"
            )

            if self.correct >= 5:

                Clock.schedule_once(
                    lambda dt:
                    self.complete_shapes(),
                    0.9
                )

            else:

                Clock.schedule_once(
                    lambda dt:
                    self.new_question(),
                    1.0
                )

        else:

            Clock.schedule_once(
                lambda dt:
                App.get_running_app().play_audio(
                    "focus_try_again.wav"
                ),
                0.5
            )

    def complete_shapes(self):

        App.get_running_app().award_star(
            "shapes"
        )

        App.get_running_app().play_audio(
            "reward_complete.wav"
        )

        self.question.text = ar(
            "أحسنت! تعرفت على الأشكال ★"
        )

        self.score_label.text = ar(
            "النشاط مكتمل"
        )


# ============================================================
# REWARDS / PROGRESS
# ============================================================

class RewardsScreen(BaseScreen):

    sections = [
        ("التركيز والانتباه", "focus"),
        ("عائلتي", "family"),
        ("الأشكال", "shapes"),
        ("الحمام", "toilet"),
        ("الوضوء", "wudu"),
        ("أريد / التواصل", "communication"),
        ("النظافة", "hygiene"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            self.build_header(
                "المكافآت والتقدم"
            )
        )

        app = App.get_running_app()

        star_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160)
        )

        star = make_label(
            "★",
            size=75,
            color=GOLD,
            size_hint_y=None,
            height=dp(90)
        )

        star_box.add_widget(star)

        total = make_label(
            f"{app.stars} نجوم",
            size=25,
            color=NAVY,
            size_hint_y=None,
            height=dp(55)
        )

        star_box.add_widget(total)

        self.root_layout.add_widget(
            star_box
        )

        if app.stars >= len(self.sections):

            message = "أحسنت يا أحمد! أكملت جميع الأنشطة!"

        else:

            message = "استمر يا أحمد! اجمع المزيد من النجوم."

        self.root_layout.add_widget(
            make_label(
                message,
                size=19,
                color=GREEN,
                size_hint_y=None,
                height=dp(55)
            )
        )

        scroll = ScrollView(
            do_scroll_x=False
        )

        grid = GridLayout(
            cols=1,
            spacing=dp(8),
            padding=dp(5),
            size_hint_y=None
        )

        grid.bind(
            minimum_height=grid.setter("height")
        )

        for title, section_id in self.sections:

            completed = section_id in app.completed

            card = RoundedCard(
                orientation="horizontal",
                card_color=(
                    0.91,
                    0.98,
                    0.93,
                    1
                ) if completed else WHITE,
                size_hint_y=None,
                height=dp(65)
            )

            icon = make_label(
                "★" if completed else "○",
                size=28,
                color=GOLD if completed else MUTED,
                size_hint_x=None,
                width=dp(55)
            )

            card.add_widget(icon)

            title_label = make_label(
                title,
                size=18,
                color=TEXT
            )

            card.add_widget(title_label)

            status = make_label(
                "مكتمل" if completed else "لم يكتمل",
                size=15,
                color=GREEN if completed else MUTED,
                size_hint_x=None,
                width=dp(80)
            )

            card.add_widget(status)

            grid.add_widget(card)

        scroll.add_widget(grid)

        self.root_layout.add_widget(
            scroll
        )

        self.refresh_stars()


# ============================================================
# MAIN APP
# ============================================================

class AhmedWorldApp(App):

    title = "Ahmed World"

    def build(self):

        Window.clearcolor = BG_COLOR

        # ----------------------------------------------------
        # Persistent progress
        # ----------------------------------------------------

        self.progress_file = os.path.join(
            self.user_data_dir,
            "progress.json"
        )

        self.store = JsonStore(
            self.progress_file
        )

        self.stars = 0
        self.completed = set()

        self.load_progress()

        # ----------------------------------------------------
        # Audio cache
        # ----------------------------------------------------

        self.sound_cache = {}
        self.current_sound = None

        # ----------------------------------------------------
        # Screen manager
        # ----------------------------------------------------

        manager = ScreenManager(
            transition=SlideTransition(
                duration=0.25
            )
        )

        manager.add_widget(
            SplashScreen(
                name="splash"
            )
        )

        manager.add_widget(
            MainMenuScreen(
                name="main_menu"
            )
        )

        manager.add_widget(
            FocusScreen(
                name="focus"
            )
        )

        manager.add_widget(
            FamilyScreen(
                name="family"
            )
        )

        manager.add_widget(
            ShapesScreen(
                name="shapes"
            )
        )

        manager.add_widget(
            ToiletScreen(
                name="toilet"
            )
        )

        manager.add_widget(
            WuduScreen(
                name="wudu"
            )
        )

        manager.add_widget(
            CommunicationScreen(
                name="communication"
            )
        )

        manager.add_widget(
            HygieneScreen(
                name="hygiene"
            )
        )

        manager.add_widget(
            RewardsScreen(
                name="rewards"
            )
        )

        manager.current = "splash"

        # Android / hardware back
        Window.bind(
            on_keyboard=self.on_keyboard
        )

        return manager

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    def load_progress(self):

        try:

            if self.store.exists("progress"):

                data = self.store.get(
                    "progress"
                )

                self.stars = int(
                    data.get("stars", 0)
                )

                self.completed = set(
                    data.get("completed", [])
                )

        except Exception:

            self.stars = 0
            self.completed = set()

    def save_progress(self):

        try:

            self.store.put(
                "progress",
                stars=self.stars,
                completed=list(
                    self.completed
                )
            )

        except Exception:
            pass

    def award_star(self, section_id):

        if section_id not in self.completed:

            self.completed.add(
                section_id
            )

            self.stars += 1

            self.save_progress()

            self.play_audio(
                "reward_star.wav"
            )

            return True

        return False

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    def play_audio(self, filename):

        path = audio_path(filename)

        if not os.path.exists(path):
            return

        try:

            if self.current_sound:

                self.current_sound.stop()

            if path not in self.sound_cache:

                sound = SoundLoader.load(
                    path
                )

                if sound:
                    self.sound_cache[path] = sound

            sound = self.sound_cache.get(path)

            if sound:

                sound.stop()
                sound.play()

                self.current_sound = sound

        except Exception:
            pass

    # --------------------------------------------------------
    # Hardware back button
    # --------------------------------------------------------

    def on_keyboard(
        self,
        window,
        key,
        scancode,
        codepoint,
        modifier
    ):

        if key == 27:

            if self.root:

                current = self.root.current

                if current != "main_menu":

                    self.root.transition = (
                        SlideTransition(
                            direction="right"
                        )
                    )

                    self.root.current = (
                        "main_menu"
                    )

                    return True

            return False

        return False


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    AhmedWorldApp().run()
