# frontend/menus/profile_menu.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class ProfileMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text="Profile", size_hint_y=0.3))
        self.add_widget(Button(text="View Profile", size_hint_y=0.3))
        self.add_widget(Button(text="Edit Wolf", size_hint_y=0.3))