# frontend/main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from frontend.map_view import WolfStepMapView
from frontend.menus.profile_menu import ProfileMenu
from frontend.menus.position_menu import PositionMenu
from frontend.menus.step_menu import StepMenu

class WolfStepApp(App):
    def build(self):
        root = FloatLayout()
        self.map_view = WolfStepMapView()
        root.add_widget(self.map_view)
        profile_menu = ProfileMenu(pos_hint={'top': 1, 'left': 0}, size_hint=(0.2, 0.2))
        root.add_widget(profile_menu)
        position_menu = PositionMenu(pos_hint={'top': 1, 'right': 1}, size_hint=(0.2, 0.2))
        root.add_widget(position_menu)
        step_menu = StepMenu(pos_hint={'center_x': 0.5, 'bottom': 0}, size_hint=(0.2, 0.2))
        root.add_widget(step_menu)
        return root

if __name__ == "__main__":
    WolfStepApp().run()