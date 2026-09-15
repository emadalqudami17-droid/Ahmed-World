# -*- coding: utf-8 -*-

import os
import random
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import (
    Color, RoundedRectangle, Rectangle,
    Ellipse, Line
)
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


# ============================================================
# FONT
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_font():
    candidates = [
        os.path.join(BASE_DIR, "Cairo-Regular.ttf"),
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
    pass


# ============================================================
# ARABIC RESHAPING
# ============================================================

try:
    import arabic_reshaper
    _RESHAPER_OK = True
except Exception:
    _RESHAPER_OK = False


def _reverse_arabic(text):
    if not text:
        return text

    lines = text.split("\n")
    result_lines = []

    for line in lines:
        if not line.strip():
            result_lines.append(line)
            continue

        words = line.split(" ")
        words.reverse()

        reversed_words = []
        for word in words:
            if not word:
                reversed_words.append("")
                continue

            first_char = word[0]
            if first_char.isdigit() or first_char in "0123456789+-*/=.,:;()[]":
                reversed_words.append(word)
            else:
                reversed_words.append(word[::-1])

        result_lines.append(" ".join(reversed_words))

    return "\n".join(result_lines)


def ar(text):
    if not text:
        return text

    if _RESHAPER_OK:
        try:
            reshaped = arabic_reshaper.reshape(text)
        except Exception:
            reshaped = text
    else:
        reshaped = text

    return _reverse_arabic(reshaped)


# ============================================================
# PATHS
# ============================================================

def asset(path):
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
# COLORS
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
# HELPERS
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
# ICON BUTTON
# ============================================================

class IconButton(ButtonBehavior, Image):

    def __init__(self, icon_file, width=50, **kwargs):
        super().__init__(
            source=image_path(icon_file),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=None,
            width=dp(width),
            **kwargs
        )

    def on_press(self):
        self.opacity = 0.6

    def on_release(self):
        self.opacity = 1.0


# ============================================================
# ROUND BUTTON
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

        self.bind(pos=self.update_background, size=self.update_background)

    def update_background(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_press(self):
        self.bg_color.rgba = self.pressed_color

    def on_release(self):
        self.bg_color.rgba = self.normal_color


# ============================================================
# ROUND CARD
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

        self.bind(pos=self.update_card, size=self.update_card)

    def update_card(self, *args):
        self.shadow_rect.pos = (self.x + dp(2), self.y - dp(2))
        self.shadow_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_press(self):
        self.bg_color.rgba = tuple(max(0, x * 0.92) for x in self.card_color)

    def on_release(self):
        self.bg_color.rgba = self.card_color


# ============================================================
# CELEBRATION WIDGET
# ============================================================

class CelebrationWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.active = False
        self._clock_event = None

    def start(self):
        self.particles = []
        self.active = True

        for _ in range(40):
            ptype = random.choice(["bubble", "star"])
            self.particles.append({
                "type": ptype,
                "x": random.uniform(0, max(1, self.width)),
                "y": self.height + random.uniform(0, 200),
                "vx": random.uniform(-80, 80),
                "vy": random.uniform(-450, -250),
                "size": random.uniform(18, 45),
                "color": random.choice([
                    (1.0, 0.75, 0.20, 1),
                    (0.30, 0.70, 1.00, 1),
                    (1.00, 0.45, 0.65, 1),
                    (0.35, 0.90, 0.55, 1),
                    (1.00, 0.55, 0.20, 1),
                ]),
                "rotation": 0,
                "rot_speed": random.uniform(-400, 400),
            })

        if self._clock_event:
            self._clock_event.cancel()
        self._clock_event = Clock.schedule_interval(self._update, 1/60.0)

    def stop(self):
        self.active = False
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        self.particles = []
        self.canvas.clear()

    def _update(self, dt):
        if not self.active:
            return
        w = self.width
        alive = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] -= 250 * dt
            p["rotation"] += p["rot_speed"] * dt
            if p["x"] < 0 or p["x"] > w:
                p["vx"] = -p["vx"]
            if p["y"] > -80:
                alive.append(p)
        self.particles = alive
        self._redraw()
        if not self.particles:
            self.stop()

    def _redraw(self):
        self.canvas.clear()
        with self.canvas:
            for p in self.particles:
                Color(*p["color"])
                if p["type"] == "bubble":
                    s = p["size"]
                    Ellipse(
                        pos=(p["x"] - s/2, p["y"] - s/2),
                        size=(s, s)
                    )
                else:
                    s = p["size"]
                    ang = math.radians(p["rotation"])
                    for offset in (0, math.pi/2):
                        dx = math.cos(ang + offset) * s/2
                        dy = math.sin(ang + offset) * s/2
                        Line(
                            points=[
                                p["x"] - dx, p["y"] - dy,
                                p["x"] + dx, p["y"] + dy,
                            ],
                            width=dp(3),
                        )


# ============================================================
# BASE SCREEN
# ============================================================

class BaseScreen(Screen):

    def on_pre_enter(self, *args):
        Window.clearcolor = BG_COLOR

    def build_header(self, title, show_back=False):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(75),
            spacing=dp(8),
            padding=(dp(10), dp(10))
        )

        header.add_widget(Widget(size_hint_x=None, width=dp(70)))

        title_label = make_label(
            title,
            size=21,
            color=NAVY,
            size_hint_y=None,
            height=dp(55),
        )
        header.add_widget(title_label)

        star_box = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(85),
            spacing=dp(2),
        )
        star_icon = Image(
            source=image_path("star.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=None,
            width=dp(26),
        )
        star_box.add_widget(star_icon)

        app = App.get_running_app()
        stars = make_label(
            f"{app.stars}",
            size=18,
            color=GOLD,
            size_hint_x=None,
            width=dp(45),
        )
        star_box.add_widget(stars)

        header.add_widget(star_box)
        self.star_header = stars

        return header

    def build_footer_buttons(self):
        footer = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(10),
            padding=(dp(15), dp(6))
        )

        back_button = IconButton("icon_back.png", width=40)
        back_button.bind(on_release=lambda *_: self.go_main())
        footer.add_widget(back_button)

        footer.add_widget(Widget())

        return footer

    def confirm_exit(self):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        message = make_label(
            "هل تريد الخروج من التطبيق؟",
            size=20,
            color=TEXT,
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(message)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(10)
        )

        cancel_btn = RoundButton(
            text="لا",
            button_color=MUTED,
            height=50
        )
        cancel_btn.bind(on_release=lambda *_: popup.dismiss())

        yes_btn = RoundButton(
            text="نعم",
            button_color=RED,
            height=50
        )
        yes_btn.bind(on_release=lambda *_: self._do_exit(popup))

        buttons.add_widget(cancel_btn)
        buttons.add_widget(yes_btn)
        content.add_widget(buttons)

        popup = Popup(
            title=ar("تأكيد"),
            title_font="Arabic",
            content=content,
            size_hint=(0.85, None),
            height=dp(230),
            auto_dismiss=False,
            separator_color=NAVY,
        )
        popup.open()

    def _do_exit(self, popup):
        popup.dismiss()
        App.get_running_app().stop()

    def exit_app(self):
        App.get_running_app().stop()

    def refresh_stars(self):
        if hasattr(self, "star_header"):
            app = App.get_running_app()
            self.star_header.text = f"{app.stars}"

    def go_main(self):
        App.get_running_app().stop_audio()
        manager = self.manager
        if manager:
            manager.transition = SlideTransition(direction="right")
            manager.current = "main_menu"


# ============================================================
# SPLASH SCREEN
# ============================================================

class SplashScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        layout.add_widget(Widget(size_hint_y=0.05))

        ahmed_image = Image(
            source=asset("app_icon.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.55
        )
        layout.add_widget(ahmed_image)

        layout.add_widget(make_label(
            "عالم أحمد", size=38, color=NAVY,
            size_hint_y=None, height=dp(70)
        ))

        layout.add_widget(make_label(
            "أهلاً أحمد!", size=28, color=GOLD,
            size_hint_y=None, height=dp(60)
        ))

        layout.add_widget(Widget(size_hint_y=0.10))

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_enter(self, *args):
        Clock.schedule_once(self.open_main, 7.0)

    def open_main(self, dt):
        if self.manager:
            self.manager.current = "main_menu"


# ============================================================
# MAIN MENU
# ============================================================

class MainMenuScreen(BaseScreen):

    sections = [
        ("icon_focus.png", "التركيز والانتباه", "focus"),
        ("icon_family.png", "عائلتي", "family"),
        ("icon_shapes.png", "الأشكال", "shapes"),
        ("icon_writing.png", "هيا نكتب", "letters"),
        ("icon_toilet.png", "الحمام", "toilet"),
        ("icon_wudu.png", "الوضوء", "wudu"),
        ("icon_communication.png", "أريد / التواصل", "communication"),
        ("icon_hygiene.png", "النظافة", "hygiene"),
        ("icon_rewards.png", "المكافآت والتقدم", "rewards"),
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

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=(dp(8), dp(5)),
            spacing=dp(6),
        )

        header.add_widget(Image(
            source=image_path("family_ahmed.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=None,
            width=dp(70)
        ))

        title_box = BoxLayout(orientation="vertical")
        title_box.add_widget(make_label("عالم أحمد", size=27, color=NAVY))
        title_box.add_widget(make_label("أهلاً أحمد! هيا نتعلم", size=17, color=MUTED))
        header.add_widget(title_box)

        app = App.get_running_app()

        star_box = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(90),
            spacing=dp(2),
        )
        star_box.add_widget(Image(
            source=image_path("star.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=None,
            width=dp(28),
        ))
        star_box.add_widget(make_label(
            f"{app.stars}", size=20, color=GOLD,
            size_hint_x=None, width=dp(50),
        ))
        header.add_widget(star_box)

        self.root_layout.add_widget(header)

        scroll = ScrollView(do_scroll_x=False)
        grid = GridLayout(
            cols=2, spacing=dp(12), padding=dp(8), size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        for index, (icon_file, title, screen_name) in enumerate(self.sections):

            completed = screen_name in app.completed

            card = RoundedCard(
                card_color=CARD_COLORS[index % len(CARD_COLORS)],
                size_hint_y=None,
                height=dp(165)
            )

            card.add_widget(Image(
                source=image_path(icon_file),
                allow_stretch=True,
                keep_ratio=True,
                size_hint_y=None,
                height=dp(65),
            ))

            card.add_widget(make_label(title, size=18, color=TEXT))

            status_box = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30),
                spacing=dp(4),
            )

            if completed:
                status_box.add_widget(Widget())
                status_box.add_widget(Image(
                    source=image_path("star.png"),
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint_x=None,
                    width=dp(20),
                ))
                status_box.add_widget(make_label(
                    "مكتمل", size=14, color=GOLD,
                    size_hint_x=None, width=dp(60),
                ))
                status_box.add_widget(Widget())
            else:
                status_box.add_widget(make_label(
                    "اضغط للبدء", size=14, color=MUTED,
                ))

            card.add_widget(status_box)

            card.bind(
                on_release=lambda instance, name=screen_name:
                self.open_section(name)
            )
            grid.add_widget(card)

        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)

        self.root_layout.add_widget(make_label(
            "اختر نشاطًا لنبدأ!", size=17, color=MUTED,
            size_hint_y=None, height=dp(36)
        ))

        exit_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
            padding=(dp(8), dp(4))
        )

        exit_row.add_widget(Widget())

        exit_icon = IconButton("icon_exit.png", width=42)
        exit_icon.bind(on_release=lambda *_: self.confirm_exit())
        exit_row.add_widget(exit_icon)

        exit_row.add_widget(make_label(
            "خروج", size=16, color=RED,
            size_hint_x=None, width=dp(60)
        ))

        exit_row.add_widget(Widget())

        self.root_layout.add_widget(exit_row)

    def exit_app(self):
        App.get_running_app().stop()

    def open_section(self, name):
        App.get_running_app().stop_audio()
        if self.manager:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = name


# ============================================================
# STEP SCREEN
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

    def on_leave(self, *args):
        App.get_running_app().stop_audio()

    def build_ui(self):

        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.build_header(self.title))

        self.progress_label = make_label(
            "", size=17, color=BLUE,
            size_hint_y=None, height=dp(35)
        )
        self.main_layout.add_widget(self.progress_label)

        self.step_image = Image(
            source="", allow_stretch=True,
            keep_ratio=True, size_hint_y=0.55
        )
        self.main_layout.add_widget(self.step_image)

        self.caption_label = make_label(
            "", size=24, color=NAVY,
            size_hint_y=None, height=dp(65)
        )
        self.main_layout.add_widget(self.caption_label)

        play_button = RoundButton(
            text="استمع مرة أخرى",
            button_color=BLUE, height=52
        )
        play_button.bind(on_release=lambda *_: self.play_current_audio())
        self.main_layout.add_widget(play_button)

        buttons = BoxLayout(
            size_hint_y=None, height=dp(58), spacing=dp(10)
        )

        self.previous_button = RoundButton(
            text="السابق", button_color=MUTED, height=52
        )
        self.previous_button.bind(on_release=lambda *_: self.previous_step())

        self.next_button = RoundButton(
            text="التالي", button_color=GREEN, height=52
        )
        self.next_button.bind(on_release=lambda *_: self.next_step())

        buttons.add_widget(self.previous_button)
        buttons.add_widget(self.next_button)
        self.main_layout.add_widget(buttons)

        self.main_layout.add_widget(self.build_footer_buttons())

        self.update_step()

    def update_step(self):

        if not self.steps:
            return

        step = self.steps[self.current_step]
        self.step_image.source = image_path(step["image"])
        self.caption_label.text = ar(step["text"])

        total = len(self.steps)
        self.progress_label.text = ar(
            f"الخطوة {self.current_step + 1} من {total}"
        )
        self.previous_button.disabled = (self.current_step == 0)

        if self.current_step == total - 1:
            self.next_button.text = ar("أكملت")
        else:
            self.next_button.text = ar("التالي")

        self.refresh_stars()

    def play_current_audio(self):
        if self.finished:
            return
        step = self.steps[self.current_step]
        App.get_running_app().play_audio(step["audio"])

    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def next_step(self):

        if self.finished:
            self.current_step = 0
            self.finished = False
            self.update_step()
            return

        if self.current_step < len(self.steps) - 1:
            App.get_running_app().play_audio("cheer.wav")
            self.current_step += 1
            Clock.schedule_once(lambda dt: self.update_step(), 0.7)
        else:
            self.finish_activity()

    def finish_activity(self):
        self.finished = True
        app = App.get_running_app()
        app.award_star(self.section_id)
        App.get_running_app().play_audio(self.complete_audio)
        self.caption_label.text = ar(self.complete_message)
        self.next_button.text = ar("ابدأ من جديد")
        self.progress_label.text = ar("أحسنت! النشاط مكتمل")


# ============================================================
# TOILET
# ============================================================

class ToiletScreen(StepScreen):
    section_id = "toilet"
    title = "الحمام"
    complete_message = "أحسنت يا أحمد! أكملت خطوات الحمام."

    steps = [
        {"image": "step1_feel.png", "audio": "audio1.wav",
         "text": "أشعر أنني أريد الذهاب إلى الحمام."},
        {"image": "step2_walk.png", "audio": "audio2.wav",
         "text": "أذهب إلى الحمام."},
        {"image": "step3_pants_down.png", "audio": "audio3.wav",
         "text": "أنزل ملابسي."},
        {"image": "step4_sit.png", "audio": "audio4.wav",
         "text": "أجلس على المرحاض."},
        {"image": "step5_clean.png", "audio": "audio5.wav",
         "text": "أنظف نفسي."},
        {"image": "step6_pants_up.png", "audio": "audio6.wav",
         "text": "أرفع ملابسي."},
        {"image": "step7_wash_hands.png", "audio": "audio7.wav",
         "text": "أغسل يدي."},
    ]


# ============================================================
# WUDU
# ============================================================

class WuduScreen(StepScreen):
    section_id = "wudu"
    title = "الوضوء"
    complete_audio = "wudu_complete.wav"
    complete_message = "أحسنت يا أحمد! أكملت الوضوء."

    steps = [
        {"image": "wudu_01_hands.png", "audio": "wudu_01_hands.wav",
         "text": "أغسل يدي."},
        {"image": "wudu_02_mouth.png", "audio": "wudu_02_mouth.wav",
         "text": "أغسل فمي."},
        {"image": "wudu_03_nose.png", "audio": "wudu_03_nose.wav",
         "text": "أغسل أنفي."},
        {"image": "wudu_04_face.png", "audio": "wudu_04_face.wav",
         "text": "أغسل وجهي."},
        {"image": "wudu_05_right_arm.png", "audio": "wudu_05_arm.wav",
         "text": "أغسل ذراعي."},
        {"image": "wudu_06_head.png", "audio": "wudu_06_head.wav",
         "text": "أمسح رأسي."},
        {"image": "wudu_07_ears.png", "audio": "wudu_07_ears.wav",
         "text": "أمسح أذني."},
        {"image": "wudu_08_feet.png", "audio": "wudu_08_feet.wav",
         "text": "أغسل قدمي."},
    ]


# ============================================================
# HYGIENE
# ============================================================

class HygieneScreen(StepScreen):
    section_id = "hygiene"
    title = "النظافة"
    complete_message = "أحسنت يا أحمد! تعلمت خطوات النظافة."

    steps = [
        {"image": "hygiene_brush_teeth.png", "audio": "hygiene_brush_teeth.wav",
         "text": "أنظف أسناني."},
        {"image": "hygiene_bath.png", "audio": "hygiene_bath.wav",
         "text": "أستحم وأنظف جسمي."},
        {"image": "hygiene_soap.png", "audio": "hygiene_soap.wav",
         "text": "أستخدم الصابون."},
        {"image": "hygiene_towel.png", "audio": "hygiene_towel.wav",
         "text": "أجفف يدي بالمنشفة."},
        {"image": "hygiene_wash_hands.png", "audio": "hygiene_wash_hands.wav",
         "text": "أغسل يدي بالماء والصابون."},
    ]


# ============================================================
# FAMILY
# ============================================================

class FamilyScreen(BaseScreen):

    people = [
        ("family_ahmed.png", "أحمد", "say_ahmed.wav"),
        ("family_dad.png", "أبي", "say_dad.wav"),
        ("family_mohamed.png", "محمد", "say_mohamed.wav"),
        ("family_milad.png", "ميلاد", "say_milad.wav"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tapped = set()
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10), spacing=dp(8)
        )
        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.tapped = set()
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header("عائلتي"))

        self.root_layout.add_widget(make_label(
            "تعرف على أفراد عائلتك",
            size=20, color=NAVY,
            size_hint_y=None, height=dp(45)
        ))

        grid = GridLayout(
            cols=2, spacing=dp(12), padding=dp(8), size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        for index, (filename, name, audio) in enumerate(self.people):

            card = RoundedCard(
                card_color=CARD_COLORS[index % len(CARD_COLORS)],
                size_hint_y=None,
                height=dp(205)
            )

            card.add_widget(Image(
                source=image_path(filename),
                allow_stretch=True,
                keep_ratio=True
            ))

            card.add_widget(make_label(
                name, size=21, color=NAVY,
                size_hint_y=None, height=dp(40)
            ))

            card.bind(
                on_release=lambda instance, i=index, snd=audio:
                self.person_selected(i, snd)
            )
            grid.add_widget(card)

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)

        self.status = make_label(
            "اضغط على صورة لسماع الاسم",
            size=16, color=MUTED,
            size_hint_y=None, height=dp(40)
        )
        self.root_layout.add_widget(self.status)

        self.root_layout.add_widget(self.build_footer_buttons())

        self.refresh_stars()

    def on_leave(self, *args):
        App.get_running_app().stop_audio()

    def person_selected(self, index, audio):
        self.tapped.add(index)
        App.get_running_app().play_audio(audio)
        if len(self.tapped) == len(self.people):
            self.status.text = ar("أحسنت! تعرفت على عائلتك")
            App.get_running_app().award_star("family")


# ============================================================
# COMMUNICATION
# ============================================================

class CommunicationScreen(BaseScreen):

    cards = [
        ("aac_water.png", "ماء", "say_water.wav"),
        ("aac_food.png", "طعام", "say_food.wav"),
        ("aac_toilet.png", "حمام", "say_toilet.wav"),
        ("aac_sleep.png", "نوم", "say_sleep.wav"),
        ("aac_help.png", "ساعدني", "say_help.wav"),
        ("aac_play.png", "أريد أن ألعب", "say_play.wav"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.used = set()
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10), spacing=dp(8)
        )
        self.add_widget(self.root_layout)

    def on_enter(self, *args):

        self.used = set()
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header("أريد / التواصل"))

        self.root_layout.add_widget(make_label(
            "اضغط على الصورة لتقول ما تريد",
            size=19, color=NAVY,
            size_hint_y=None, height=dp(42)
        ))

        scroll = ScrollView(do_scroll_x=False)
        grid = GridLayout(
            cols=2,
            spacing=dp(12),
            padding=dp(8),
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        for index, (filename, text, audio) in enumerate(self.cards):

            card = RoundedCard(
                card_color=CARD_COLORS[index % len(CARD_COLORS)],
                size_hint_y=None,
                height=dp(200)
            )

            card.add_widget(Image(
                source=image_path(filename),
                allow_stretch=True,
                keep_ratio=True
            ))

            card.add_widget(make_label(
                text, size=18, color=TEXT,
                size_hint_y=None, height=dp(48)
            ))

            card.bind(
                on_release=lambda instance, i=index, snd=audio:
                self.communication_selected(i, snd)
            )
            grid.add_widget(card)

        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)

        self.status = make_label(
            f"0 / {len(self.cards)}",
            size=16, color=MUTED,
            size_hint_y=None, height=dp(38)
        )
        self.root_layout.add_widget(self.status)

        self.root_layout.add_widget(self.build_footer_buttons())

        self.refresh_stars()

    def on_leave(self, *args):
        App.get_running_app().stop_audio()

    def communication_selected(self, index, audio):
        self.used.add(index)
        App.get_running_app().play_audio(audio)
        self.status.text = ar(f"{len(self.used)} / {len(self.cards)}")
        if len(self.used) == len(self.cards):
            self.status.text = ar("أحسنت! تعلمت كلمات التواصل")
            App.get_running_app().award_star("communication")


# ============================================================
# FOCUS
# ============================================================

class FocusScreen(BaseScreen):

    targets = [
        {"id": "ahmed", "image": "family_ahmed.png",
         "audio": "focus_find_ahmed.wav", "name": "أحمد"},
        {"id": "dad", "image": "family_dad.png",
         "audio": "focus_find_dad.wav", "name": "أبي"},
        {"id": "mohamed", "image": "family_mohamed.png",
         "audio": "focus_find_mohamed.wav", "name": "محمد"},
        {"id": "milad", "image": "family_milad.png",
         "audio": "focus_find_milad.wav", "name": "ميلاد"},
        {"id": "apple", "image": "focus_apple.png",
         "audio": "focus_find_apple.wav", "name": "التفاحة"},
        {"id": "car", "image": "focus_car.png",
         "audio": "focus_find_car.wav", "name": "السيارة"},
        {"id": "cat", "image": "focus_cat.png",
         "audio": "focus_find_cat.wav", "name": "القطة"},
        {"id": "dog", "image": "focus_dog.png",
         "audio": "focus_find_dog.wav", "name": "الكلب"},
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.rounds = 0
        self.current_target = None
        self.options = []
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10), spacing=dp(7)
        )
        self.add_widget(self.root_layout)

    def on_enter(self, *args):
        self.score = 0
        self.rounds = 0
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header("التركيز والانتباه"))

        self.root_layout.add_widget(make_label(
            "انظر جيدًا واختر الصحيح",
            size=20, color=NAVY,
            size_hint_y=None, height=dp(42)
        ))

        self.question = make_label(
            "استمع...", size=25, color=BLUE,
            size_hint_y=None, height=dp(55)
        )
        self.root_layout.add_widget(self.question)

        self.options_grid = GridLayout(
            cols=3, spacing=dp(10), padding=dp(6), size_hint_y=0.65
        )
        self.root_layout.add_widget(self.options_grid)

        self.score_label = make_label(
            "0 / 5", size=17, color=MUTED,
            size_hint_y=None, height=dp(35)
        )
        self.root_layout.add_widget(self.score_label)

        self.root_layout.add_widget(self.build_footer_buttons())

        self.new_round()

    def on_leave(self, *args):
        App.get_running_app().stop_audio()

    def new_round(self):
        self.current_target = random.choice(self.targets)
        others = [t for t in self.targets if t["id"] != self.current_target["id"]]
        self.options = random.sample(others, 2) + [self.current_target]
        random.shuffle(self.options)

        self.options_grid.clear_widgets()

        for item in self.options:
            card = RoundedCard(
                card_color=LIGHT_BLUE,
                size_hint_y=None,
                height=dp(180)
            )
            card.add_widget(Image(
                source=image_path(item["image"]),
                allow_stretch=True,
                keep_ratio=True
            ))
            card.add_widget(make_label(
                item["name"], size=14, color=MUTED,
                size_hint_y=None, height=dp(32)
            ))
            card.bind(
                on_release=lambda instance, selected=item:
                self.check_answer(selected)
            )
            self.options_grid.add_widget(card)

        Clock.schedule_once(lambda dt: self.ask_question(), 0.3)

    def ask_question(self):
        App.get_running_app().play_audio("focus_look.wav")
        Clock.schedule_once(
            lambda dt: App.get_running_app().play_audio(
                self.current_target["audio"]
            ),
            0.8
        )
        self.question.text = ar("أين هو؟")

    def check_answer(self, selected):
        if self.current_target is None:
            return
        if selected["id"] == self.current_target["id"]:
            self.score += 1
            self.rounds += 1
            App.get_running_app().play_audio("cheer.wav")
            self.score_label.text = ar(f"{self.score} / 5")
            if self.score >= 5:
                App.get_running_app().award_star("focus")
                Clock.schedule_once(lambda dt: self.finish_focus(), 0.7)
            else:
                Clock.schedule_once(lambda dt: self.new_round(), 0.8)
        else:
            App.get_running_app().play_audio("focus_try_again.wav")

    def finish_focus(self):
        App.get_running_app().play_audio("reward_complete.wav")
        self.question.text = ar("أحسنت يا أحمد! ممتاز!")
        self.score_label.text = ar("النشاط مكتمل")


# ============================================================
# SHAPES
# ============================================================

class ShapesScreen(BaseScreen):

    shapes = [
        ("circle", "دائرة", "shape_circle.wav"),
        ("square", "مربع", "shape_square.wav"),
        ("triangle", "مثلث", "shape_triangle.wav"),
        ("rectangle", "مستطيل", "shape_rectangle.wav"),
        ("star", "نجمة", "shape_star.wav"),
        ("heart", "قلب", "shape_heart.wav"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.correct = 0
        self.target = None
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10), spacing=dp(7)
        )
        self.add_widget(self.root_layout)

    def on_enter(self, *args):
        self.correct = 0
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header("الأشكال"))

        target_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(180),
            padding=dp(5),
        )

        self.target_image = Image(
            source=image_path("shape_circle_blue.png"),
            allow_stretch=True,
            keep_ratio=True,
        )
        target_box.add_widget(self.target_image)

        self.root_layout.add_widget(target_box)

        self.question = make_label(
            "اختر الشكل الصحيح",
            size=21, color=NAVY,
            size_hint_y=None, height=dp(42)
        )
        self.root_layout.add_widget(self.question)

        self.grid = GridLayout(
            cols=3, spacing=dp(10), padding=dp(6)
        )
        self.root_layout.add_widget(self.grid)

        self.score_label = make_label(
            "0 / 5", size=17, color=MUTED,
            size_hint_y=None, height=dp(35)
        )
        self.root_layout.add_widget(self.score_label)

        self.root_layout.add_widget(self.build_footer_buttons())

        self.new_question()

    def on_leave(self, *args):
        App.get_running_app().stop_audio()

    def new_question(self):
        self.target = random.choice(self.shapes)
        shape_name = self.target[0]

        self.target_image.source = image_path(
            f"shape_{shape_name}_blue.png"
        )

        self.grid.clear_widgets()

        options = list(self.shapes)
        random.shuffle(options)

        for shape_type, name, audio in options:
            card = RoundedCard(
                card_color=WHITE,
                size_hint_y=None,
                height=dp(145)
            )
            card.add_widget(Image(
                source=image_path(f"shape_{shape_type}_gold.png"),
                allow_stretch=True,
                keep_ratio=True,
            ))
            card.add_widget(make_label(
                name, size=14, color=TEXT,
                size_hint_y=None, height=dp(30)
            ))
            card.bind(
                on_release=lambda instance, st=shape_type, snd=audio:
                self.check_shape(st, snd)
            )
            self.grid.add_widget(card)

        App.get_running_app().play_audio("find_shape.wav")

    def check_shape(self, selected_shape, audio):
        if self.target is None:
            return
        App.get_running_app().play_audio(audio)
        if selected_shape == self.target[0]:
            self.correct += 1
            Clock.schedule_once(
                lambda dt: App.get_running_app().play_audio("cheer.wav"),
                0.5
            )
            self.score_label.text = ar(f"{self.correct} / 5")
            if self.correct >= 5:
                Clock.schedule_once(lambda dt: self.complete_shapes(), 0.9)
            else:
                Clock.schedule_once(lambda dt: self.new_question(), 1.0)
        else:
            Clock.schedule_once(
                lambda dt: App.get_running_app().play_audio(
                    "focus_try_again.wav"
                ),
                0.5
            )

    def complete_shapes(self):
        App.get_running_app().award_star("shapes")
        App.get_running_app().play_audio("reward_complete.wav")
        self.question.text = ar("أحسنت! تعرفت على الأشكال")
        self.score_label.text = ar("النشاط مكتمل")


# ============================================================
# REWARDS
# ============================================================

class RewardsScreen(BaseScreen):

    sections = [
        ("التركيز والانتباه", "focus"),
        ("عائلتي", "family"),
        ("الأشكال", "shapes"),
        ("أريد / التواصل", "communication"),
        ("الحمام", "toilet"),
        ("الوضوء", "wudu"),
        ("النظافة", "hygiene"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(12), spacing=dp(8)
        )
        self.add_widget(self.root_layout)

    def on_enter(self, *args):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header("المكافآت والتقدم"))

        app = App.get_running_app()

        star_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160)
        )

        star_box.add_widget(Image(
            source=image_path("star.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            height=dp(90),
        ))

        star_box.add_widget(make_label(
            f"{app.stars} نجوم",
            size=25, color=NAVY,
            size_hint_y=None, height=dp(55)
        ))
        self.root_layout.add_widget(star_box)

        if app.stars >= len(self.sections):
            message = "أحسنت يا أحمد! أكملت جميع الأنشطة!"
        else:
            message = "استمر يا أحمد! اجمع المزيد من النجوم."

        self.root_layout.add_widget(make_label(
            message, size=19, color=GREEN,
            size_hint_y=None, height=dp(55)
        ))

        scroll = ScrollView(do_scroll_x=False)
        grid = GridLayout(
            cols=1, spacing=dp(8), padding=dp(5), size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        for title, section_id in self.sections:
            completed = section_id in app.completed
            card = RoundedCard(
                orientation="horizontal",
                card_color=(0.91, 0.98, 0.93, 1) if completed else WHITE,
                size_hint_y=None,
                height=dp(65)
            )
            card.add_widget(Image(
                source=image_path(
                    "star.png" if completed else "star_empty.png"
                ),
                allow_stretch=True,
                keep_ratio=True,
                size_hint_x=None,
                width=dp(45),
            ))
            card.add_widget(make_label(title, size=18, color=TEXT))
            card.add_widget(make_label(
                "مكتمل" if completed else "لم يكتمل",
                size=15,
                color=GREEN if completed else MUTED,
                size_hint_x=None,
                width=dp(80),
            ))
            grid.add_widget(card)

        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)

        self.root_layout.add_widget(self.build_footer_buttons())

        self.refresh_stars()


# ============================================================
# LETTERS DATA
# ============================================================

LETTERS_DATA = [
    {"id": "alef",  "letter": "أ",  "name": "ألف",  "word": "أسد",   "enabled": True},
    {"id": "baa",   "letter": "ب",  "name": "باء",  "word": "بطة",   "enabled": True},
    {"id": "taa",   "letter": "ت",  "name": "تاء",  "word": "تفاحة", "enabled": True},
    {"id": "thaa",  "letter": "ث",  "name": "ثاء",  "word": "ثعلب",  "enabled": False},
    {"id": "jeem",  "letter": "ج",  "name": "جيم",  "word": "جمل",   "enabled": False},
    {"id": "haa",   "letter": "ح",  "name": "حاء",  "word": "حصان",  "enabled": False},
    {"id": "khaa",  "letter": "خ",  "name": "خاء",  "word": "خروف",  "enabled": False},
    {"id": "dal",   "letter": "د",  "name": "دال",  "word": "دب",    "enabled": False},
    {"id": "thal",  "letter": "ذ",  "name": "ذال",  "word": "ذئب",   "enabled": False},
    {"id": "raa",   "letter": "ر",  "name": "راء",  "word": "رمان",  "enabled": False},
    {"id": "zay",   "letter": "ز",  "name": "زاي",  "word": "زرافة", "enabled": False},
    {"id": "seen",  "letter": "س",  "name": "سين",  "word": "سمكة",  "enabled": False},
    {"id": "sheen", "letter": "ش",  "name": "شين",  "word": "شمس",   "enabled": False},
    {"id": "sad",   "letter": "ص",  "name": "صاد",  "word": "صقر",   "enabled": False},
    {"id": "dad",   "letter": "ض",  "name": "ضاد",  "word": "ضفدع",  "enabled": False},
    {"id": "taa2",  "letter": "ط",  "name": "طاء",  "word": "طائرة", "enabled": False},
    {"id": "zaa",   "letter": "ظ",  "name": "ظاء",  "word": "ظرف",   "enabled": False},
    {"id": "ain",   "letter": "ع",  "name": "عين",  "word": "عصفور", "enabled": False},
    {"id": "ghain", "letter": "غ",  "name": "غين",  "word": "غزال",  "enabled": False},
    {"id": "faa",   "letter": "ف",  "name": "فاء",  "word": "فيل",   "enabled": False},
    {"id": "qaf",   "letter": "ق",  "name": "قاف",  "word": "قمر",   "enabled": False},
    {"id": "kaf",   "letter": "ك",  "name": "كاف",  "word": "كتاب",  "enabled": False},
    {"id": "lam",   "letter": "ل",  "name": "لام",  "word": "ليمون", "enabled": False},
    {"id": "meem",  "letter": "م",  "name": "ميم",  "word": "موز",   "enabled": False},
    {"id": "noon",  "letter": "ن",  "name": "نون",  "word": "نمر",   "enabled": False},
    {"id": "haa2",  "letter": "ه",  "name": "هاء",  "word": "هاتف",  "enabled": False},
    {"id": "waw",   "letter": "و",  "name": "واو",  "word": "وردة",  "enabled": False},
    {"id": "yaa",   "letter": "ي",  "name": "ياء",  "word": "يد",    "enabled": False},
]


# ============================================================
# LETTERS LIST SCREEN
# ============================================================

class LettersListScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )
        self.add_widget(self.root_layout)

    def on_enter(self, *args):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header("هيا نكتب"))

        self.root_layout.add_widget(make_label(
            "اختر حرفاً لتتعلمه",
            size=19, color=NAVY,
            size_hint_y=None, height=dp(45)
        ))

        scroll = ScrollView(do_scroll_x=False)
        grid = GridLayout(
            cols=4,
            spacing=dp(10),
            padding=dp(8),
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        app = App.get_running_app()

        for letter_data in LETTERS_DATA:
            letter_id = letter_data["id"]
            is_completed = f"letter_{letter_id}" in app.completed
            is_enabled = letter_data["enabled"]

            if not is_enabled:
                card_color = (0.90, 0.90, 0.92, 1)
            elif is_completed:
                card_color = (0.91, 0.98, 0.93, 1)
            else:
                card_color = (0.89, 0.95, 1.00, 1)

            card = RoundedCard(
                card_color=card_color,
                size_hint_y=None,
                height=dp(130)
            )

            letter_color = NAVY if is_enabled else MUTED

            card.add_widget(make_label(
                letter_data["letter"],
                size=60,
                color=letter_color,
                size_hint_y=None,
                height=dp(80)
            ))

            card.add_widget(make_label(
                letter_data["name"],
                size=14,
                color=letter_color,
                size_hint_y=None,
                height=dp(28)
            ))

            if is_completed:
                card.add_widget(make_label(
                    "★", size=14, color=GOLD,
                    size_hint_y=None, height=dp(22)
                ))
            elif not is_enabled:
                card.add_widget(make_label(
                    "🔒", size=14, color=MUTED,
                    size_hint_y=None, height=dp(22)
                ))

            if is_enabled:
                card.bind(
                    on_release=lambda instance, data=letter_data:
                    self.open_letter(data)
                )

            grid.add_widget(card)

        scroll.add_widget(grid)
        self.root_layout.add_widget(scroll)

        self.root_layout.add_widget(self.build_footer_buttons())
        self.refresh_stars()

    def on_leave(self, *args):
        App.get_running_app().stop_audio()

    def open_letter(self, letter_data):
        app = App.get_running_app()
        app.current_letter = letter_data
        app.stop_audio()

        if self.manager:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "letter_lesson"


# ============================================================
# DRAWING AREA (يستخدم صور PNG)
# ============================================================

class DrawingArea(Widget):
    """منطقة لرسم الحرف مباشرة فوق صورته."""

    def __init__(self, letter_id="alef", **kwargs):
        super().__init__(**kwargs)

        self.letter_id = letter_id
        self._last_x = None
        self._last_y = None

        # صورة الحرف الباهت (مع نقطة البداية والسهم)
        self.letter_image = Image(
            source=image_path(
                f"letters/letter_{letter_id}_trace.png"
            ),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
        )
        self.add_widget(self.letter_image)

        self.bind(pos=self._update_children, size=self._update_children)

        # الرسم فوق كل شيء
        with self.canvas.after:
            Color(*BLUE)

    def _update_children(self, *args):
        self.letter_image.pos = self.pos
        self.letter_image.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas.after:
                Color(*BLUE)
                Line(
                    points=[touch.x, touch.y, touch.x + 0.5, touch.y + 0.5],
                    width=dp(18),
                    cap="round",
                    joint="round"
                )
            self._last_x = touch.x
            self._last_y = touch.y
            return True
        return False

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and self._last_x is not None:
            with self.canvas.after:
                Color(*BLUE)
                Line(
                    points=[self._last_x, self._last_y, touch.x, touch.y],
                    width=dp(18),
                    cap="round",
                    joint="round"
                )
            self._last_x = touch.x
            self._last_y = touch.y
            return True
        return False

    def on_touch_up(self, touch):
        self._last_x = None
        self._last_y = None
        return False

    def clear(self):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*BLUE)


# ============================================================
# LETTER LESSON SCREEN
# ============================================================

class LetterLessonScreen(BaseScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_stage = 0
        self.letter_data = None

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )
        self.add_widget(self.root_layout)

        self.celebration = CelebrationWidget()
        self.add_widget(self.celebration)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        app = App.get_running_app()
        self.letter_data = getattr(app, "current_letter", LETTERS_DATA[0])
        self.current_stage = 0
        self.build_stage()

    def on_leave(self, *args):
        App.get_running_app().stop_audio()
        self.celebration.stop()

    def build_stage(self):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(
            self.build_header(f"حرف {self.letter_data['name']}")
        )

        if self.current_stage == 0:
            self.build_recognition_stage()
        elif self.current_stage == 1:
            self.build_writing_stage()
        elif self.current_stage == 2:
            self.build_example_stage()

    def build_recognition_stage(self):
        self.root_layout.add_widget(make_label(
            "المرحلة 1: تعرّف على الحرف",
            size=16, color=MUTED,
            size_hint_y=None, height=dp(30)
        ))

        self.root_layout.add_widget(make_label(
            self.letter_data["letter"],
            size=180,
            color=NAVY,
            size_hint_y=0.65
        ))

        self.root_layout.add_widget(make_label(
            self.letter_data["name"],
            size=32,
            color=GOLD,
            size_hint_y=None,
            height=dp(50)
        ))

        next_btn = RoundButton(
            text="التالي",
            button_color=GREEN,
            height=55
        )
        next_btn.bind(on_release=lambda *_: self.next_stage())
        self.root_layout.add_widget(next_btn)

        self.root_layout.add_widget(self.build_footer_buttons())

    def build_writing_stage(self):
        self.root_layout.add_widget(make_label(
            "المرحلة 2: اكتب الحرف",
            size=16, color=MUTED,
            size_hint_y=None, height=dp(30)
        ))

        # منطقة الرسم (تستخدم صورة الحرف + نقطة البداية)
        self.drawing_area = DrawingArea(
            letter_id=self.letter_data["id"],
            size_hint_y=0.8,
        )
        self.root_layout.add_widget(self.drawing_area)

        self.root_layout.add_widget(make_label(
            "اتبع النقطة الخضراء وارسم فوق الحرف",
            size=15, color=MUTED,
            size_hint_y=None, height=dp(30)
        ))

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )

        clear_btn = RoundButton(
            text="مسح",
            button_color=MUTED,
            height=55
        )
        clear_btn.bind(on_release=lambda *_: self.drawing_area.clear())

        done_btn = RoundButton(
            text="أكملت",
            button_color=GREEN,
            height=55
        )
        done_btn.bind(on_release=lambda *_: self.complete_letter())

        buttons.add_widget(clear_btn)
        buttons.add_widget(done_btn)
        self.root_layout.add_widget(buttons)

        self.root_layout.add_widget(self.build_footer_buttons())

    def build_example_stage(self):
        self.root_layout.add_widget(make_label(
            "المرحلة 3: مثال",
            size=16, color=MUTED,
            size_hint_y=None, height=dp(30)
        ))

        self.root_layout.add_widget(Widget(size_hint_y=0.1))

        self.root_layout.add_widget(make_label(
            self.letter_data["letter"],
            size=110,
            color=NAVY,
            size_hint_y=None,
            height=dp(140)
        ))

        self.root_layout.add_widget(make_label(
            "=",
            size=50,
            color=MUTED,
            size_hint_y=None,
            height=dp(70)
        ))

        self.root_layout.add_widget(make_label(
            self.letter_data["word"],
            size=70,
            color=GOLD,
            size_hint_y=None,
            height=dp(110)
        ))

        self.root_layout.add_widget(make_label(
            f"يبدأ بحرف {self.letter_data['name']}",
            size=22,
            color=MUTED,
            size_hint_y=None,
            height=dp(50)
        ))

        self.root_layout.add_widget(Widget(size_hint_y=0.1))

        finish_btn = RoundButton(
            text="أنهيت الدرس",
            button_color=GOLD,
            height=55
        )
        finish_btn.bind(on_release=lambda *_: self.finish_lesson())
        self.root_layout.add_widget(finish_btn)

        self.root_layout.add_widget(self.build_footer_buttons())

    def next_stage(self):
        if self.current_stage < 2:
            self.current_stage += 1
            self.build_stage()
        else:
            self.finish_lesson()

    def complete_letter(self):
        self.current_stage = 2
        self.build_stage()

    def finish_lesson(self):
        app = App.get_running_app()
        app.award_star(f"letter_{self.letter_data['id']}")
        app.play_audio("cheer.wav")

        self.celebration.start()

        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.build_header(
            f"حرف {self.letter_data['name']}"
        ))

        self.root_layout.add_widget(make_label(
            "★",
            size=100,
            color=GOLD,
            size_hint_y=0.35
        ))

        self.root_layout.add_widget(make_label(
            "أحسنت يا أحمد!",
            size=32,
            color=GREEN,
            size_hint_y=None,
            height=dp(70)
        ))

        self.root_layout.add_widget(make_label(
            f"تعلمت حرف {self.letter_data['name']}",
            size=22,
            color=NAVY,
            size_hint_y=None,
            height=dp(50)
        ))

        Clock.schedule_once(self._return_to_list, 3.5)

    def _return_to_list(self, dt):
        self.celebration.stop()
        if self.manager:
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = "letters"


# ============================================================
# MAIN APP
# ============================================================

class AhmedWorldApp(App):

    title = "Ahmed World"

    def build(self):
        Window.clearcolor = BG_COLOR

        self.progress_file = os.path.join(
            self.user_data_dir, "progress.json"
        )
        self.store = JsonStore(self.progress_file)
        self.stars = 0
        self.completed = set()
        self.load_progress()

        self.sound_cache = {}
        self.current_sound = None
        self.current_letter = None

        manager = ScreenManager(
            transition=SlideTransition(duration=0.25)
        )

        manager.add_widget(SplashScreen(name="splash"))
        manager.add_widget(MainMenuScreen(name="main_menu"))
        manager.add_widget(FocusScreen(name="focus"))
        manager.add_widget(FamilyScreen(name="family"))
        manager.add_widget(ShapesScreen(name="shapes"))
        manager.add_widget(ToiletScreen(name="toilet"))
        manager.add_widget(WuduScreen(name="wudu"))
        manager.add_widget(CommunicationScreen(name="communication"))
        manager.add_widget(HygieneScreen(name="hygiene"))
        manager.add_widget(RewardsScreen(name="rewards"))
        manager.add_widget(LettersListScreen(name="letters"))
        manager.add_widget(LetterLessonScreen(name="letter_lesson"))

        manager.current = "splash"

        Window.bind(on_keyboard=self.on_keyboard)

        return manager

    def load_progress(self):
        try:
            if self.store.exists("progress"):
                data = self.store.get("progress")
                self.stars = int(data.get("stars", 0))
                self.completed = set(data.get("completed", []))
        except Exception:
            self.stars = 0
            self.completed = set()

    def save_progress(self):
        try:
            self.store.put(
                "progress",
                stars=self.stars,
                completed=list(self.completed)
            )
        except Exception:
            pass

    def award_star(self, section_id):
        if section_id not in self.completed:
            self.completed.add(section_id)
            self.stars += 1
            self.save_progress()
            self.play_audio("reward_star.wav")
            return True
        return False

    def play_audio(self, filename):
        path = audio_path(filename)
        if not os.path.exists(path):
            return
        try:
            if self.current_sound:
                self.current_sound.stop()
            if path not in self.sound_cache:
                sound = SoundLoader.load(path)
                if sound:
                    self.sound_cache[path] = sound
            sound = self.sound_cache.get(path)
            if sound:
                sound.stop()
                sound.play()
                self.current_sound = sound
        except Exception:
            pass

    def stop_audio(self):
        try:
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound = None
        except Exception:
            pass

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.root:
                current = self.root.current
                if current == "splash":
                    return True
                elif current != "main_menu":
                    self.stop_audio()
                    self.root.transition = SlideTransition(direction="right")
                    self.root.current = "main_menu"
                    return True
                else:
                    main_screen = self.root.get_screen("main_menu")
                    main_screen.confirm_exit()
                    return True
            return False
        return False


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    AhmedWorldApp().run()
