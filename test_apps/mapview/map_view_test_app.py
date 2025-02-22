# File: test_apps/mapview/map_view_test_app.py
from kivy.app import App
from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import os

class WolfStepMapApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initial coordinates (New York City as an example)
        self.lat = 40.730610
        self.lon = -73.935242
        self.marker = None

    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical')

        # Custom night-themed MapSource (CartoDB Dark)
        dark_map_source = MapSource(
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
            cache_key="osm-dark",
            tile_size=256,
            min_zoom=0,
            max_zoom=19,
            attribution="© OpenStreetMap contributors, © CartoDB"
        )

        # MapView setup with custom source
        self.map_view = MapView(
            lat=self.lat,
            lon=self.lon,
            zoom=15,  # Zoom level (higher = closer)
            map_source=dark_map_source
        )

        # Add initial wolf marker
        self.marker = MapMarker(
            lat=self.lat,
            lon=self.lon,
            source="wolf_icon.png"  # Placeholder for your pixel art wolf
        )
        self.map_view.add_marker(self.marker)

        # Add map to layout
        layout.add_widget(self.map_view)

        # Add a simple status label
        self.status_label = Label(
            text=f"Lat: {self.lat:.6f}, Lon: {self.lon:.6f}",
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.status_label)

        # Simulate position updates every 2 seconds
        Clock.schedule_interval(self.update_position, 2.0)

        return layout

    def update_position(self, dt):
        # Simulate movement (e.g., walking east)
        self.lon += 0.001  # Small increment in longitude
        self.lat += 0.0005  # Small increment in latitude

        # Update marker position
        if self.marker:
            self.map_view.remove_marker(self.marker)
            self.marker = MapMarker(
                lat=self.lat,
                lon=self.lon,
                source="wolf_icon.png"
            )
            self.map_view.add_marker(self.marker)

        # Center map on new position
        self.map_view.center_on(self.lat, self.lon)

        # Update status label
        self.status_label.text = f"Lat: {self.lat:.6f}, Lon: {self.lon:.6f}"

if __name__ == "__main__":
    # Ensure Kivy can find assets (optional, adjust path if needed)
    os.environ["KIVY_IMAGE"] = "pil"  # Use PIL for image loading
    WolfStepMapApp().run()