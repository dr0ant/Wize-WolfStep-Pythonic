# frontend/menus/step_menu.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior

class StepMenu(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Image(source="frontend/assets/wolf_footprint_white.png", size_hint_y=0.7))
        self.step_label = Label(text="Steps: 0", size_hint_y=0.3)  # Store reference for updates
        self.add_widget(self.step_label)
        self.step_count = 0  # Track steps

    def on_press(self):
        """Handle click event."""
        self.step_count += 1  # Increment step count
        self.step_label.text = f"Steps: {self.step_count}"  # Update label
        print(f"StepMenu clicked! Steps: {self.step_count}")  # Debug output