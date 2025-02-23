# frontend/map_view.py
from kivy_garden.mapview import MapView, MapSource
from kivy.utils import platform
from kivy.clock import Clock
from frontend.markers.user_marker import UserMarker

class WolfStepMapView(MapView):
    def __init__(self, position_menu=None, **kwargs):
        dark_map_source = MapSource(
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
            cache_key="osm-dark",
            tile_size=256,
            min_zoom=0,
            max_zoom=19,
            attribution="© OpenStreetMap contributors, © CartoDB"
        )

        # Initialize with default position (NYC)
        super().__init__(lat=40.730610, lon=-73.935242, zoom=15, map_source=dark_map_source, **kwargs)
        
        self.position_menu = position_menu
        self.gps_initialized = False

        # Initialize user marker
        self.user_marker = UserMarker(map_view=self, lat=self.lat, lon=self.lon)
        self.add_widget(self.user_marker)

        # Schedule GPS initialization
        Clock.schedule_once(self.initialize_gps, 0)
        print("MapView initialized with default position - Lat: 40.730610, Lon: -73.935242")

    def initialize_gps(self, dt):
        """Initialize GPS and attempt to set initial position."""
        if platform == "macosx":
            try:
                from frontend.utils.macos_gps import MacOSGPS
                self.macos_gps = MacOSGPS(on_location=self.on_location)
                print("MacOS GPS initialization scheduled")
                self.gps_initialized = True
            except ImportError as e:
                print(f"MacOS GPS ImportError: {e}, switching to simulation")
                Clock.schedule_interval(self.simulate_position, 2.0)
        elif platform in ["android", "ios"]:
            try:
                from plyer import gps
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                gps.start(minTime=1000, minDistance=1)
                print("Mobile GPS initialized")
                self.gps_initialized = True
            except Exception as e:
                print(f"Mobile GPS error: {e}, switching to simulation")
                Clock.schedule_interval(self.simulate_position, 2.0)
        else:
            print("Platform not supported for GPS, using simulation")
            Clock.schedule_interval(self.simulate_position, 2.0)

    def on_location(self, **kwargs):
        """Handle GPS location updates."""
        self.lat = kwargs.get('lat', self.lat)
        self.lon = kwargs.get('lon', self.lon)
        print(f"GPS Update - Lat: {self.lat}, Lon: {self.lon}")
        self.update_marker_and_center()
        if self.position_menu:
            self.position_menu.update_position(self.lat, self.lon)

    def on_status(self, status):
        """Display GPS status (mobile only)."""
        print(f"GPS Status: {status}")

    def simulate_position(self, dt):
        """Simulate position updates."""
        self.lat += 0.0005
        self.lon += 0.001
        print(f"Simulation Update - Lat: {self.lat}, Lon: {self.lon}")
        self.update_marker_and_center()
        if self.position_menu:
            self.position_menu.update_position(self.lat, self.lon)

    def update_marker_and_center(self):
        """Update marker position and center map."""
        self.user_marker.update_position(self.lat, self.lon)
        self.center_on(self.lat, self.lon)