# frontend/map_view.py
from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivy.clock import Clock

class WolfStepMapView(MapView):
    def __init__(self, **kwargs):
        # Custom dark map source
        dark_map_source = MapSource(
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
            cache_key="osm-dark",
            tile_size=256,
            min_zoom=0,
            max_zoom=19,
            attribution="© OpenStreetMap contributors, © CartoDB"
        )

        super().__init__(
            lat=40.730610,  # NYC as default
            lon=-73.935242,
            zoom=15,
            map_source=dark_map_source,
            **kwargs
        )

        # Add wolf marker
        self.marker = MapMarker(lat=40.730610, lon=-73.935242, source="frontend/assets/wolf_icon.png")
        self.add_marker(self.marker)

        # Simulate movement
        Clock.schedule_interval(self.update_position, 2.0)

    def update_position(self, dt):
        self.marker.lon += 0.001
        self.marker.lat += 0.0005
        self.center_on(self.marker.lat, self.marker.lon)