# frontend/menus/step_menu.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

class StepMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Image(source="frontend/assets/wolf_footprint.png", size_hint_y=0.7))
        self.add_widget(Label(text="Steps: 0", size_hint_y=0.3))