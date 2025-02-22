# frontend/menus/position_menu.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class PositionMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.lat_label = Label(text="Lat: 40.730610", size_hint_y=0.5)
        self.lon_label = Label(text="Lon: -73.935242", size_hint_y=0.5)
        self.add_widget(self.lat_label)
        self.add_widget(self.lon_label)

    def update_position(self, lat, lon):
        self.lat_label.text = f"Lat: {lat:.6f}"
        self.lon_label.text = f"Lon: {lon:.6f}"