from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivy.utils import platform
from kivy.clock import Clock
from plyer import gps
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse


class WolfStepMapView(MapView):
    def __init__(self, position_menu=None, **kwargs):
        # Définition de la carte en mode sombre
        dark_map_source = MapSource(
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
            cache_key="osm-dark",
            tile_size=256,
            min_zoom=0,
            max_zoom=19,
            attribution="© OpenStreetMap contributors, © CartoDB"
        )

        super().__init__(zoom=15, map_source=dark_map_source, **kwargs)
        
        self.position_menu = position_menu
        self.marker = None
        
        # Initialisation de la carte après construction complète du widget
        Clock.schedule_once(self.initialize_map, 0)

    def initialize_map(self, dt):
        """Initialise la carte avec une position par défaut et le GPS."""
        self.update_marker_icon()
        self.add_marker(self.marker)

        # Start GPS after widget is constructed
        self.init_gps()

    def init_gps(self):
        """Initialiser le GPS basé sur la plateforme."""
        if platform == "android" or platform == "ios":
            try:
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                gps.start(minTime=1000, minDistance=1)  # Update every 1s, min distance 1m
                print("GPS initialized on mobile")
            except (NotImplementedError, ModuleNotFoundError) as e:
                print(f"GPS error on mobile: {e}, switching to simulation.")
                Clock.schedule_interval(self.simulate_position, 2.0)

        elif platform == "macosx":
            try:
                from frontend.utils.macos_gps import MacOSGPS
                self.macos_gps = MacOSGPS(on_location=self.on_location)  # start_gps is called in constructor
                print("self.macos_gps : ", self.macos_gps)
                print("Type of macos_gps: ", type(self.macos_gps))
                print("Attributes of macos_gps: ", dir(self.macos_gps))
                print("Using CoreLocation for macOS GPS")
            except ImportError as e:
                print(f"MacOS GPS error: {e}, switching to simulation.")
                Clock.schedule_interval(self.simulate_position, 2.0)

        else:
            print("GPS not supported on this platform, using default position.")
            Clock.schedule_interval(self.simulate_position, 2.0)

    def on_location(self, **kwargs):
        """Callback pour la mise à jour de la position GPS."""
        self.lat = kwargs.get('lat', self.lat)
        self.lon = kwargs.get('lon', self.lon)
        self.update_marker_and_center()
        if self.position_menu:
            self.position_menu.update_position(self.lat, self.lon)

    def on_status(self, status):
        """Affiche le statut du GPS."""
        print(f"Statut GPS : {status}")

    def simulate_position(self, dt):
        """Simule une mise à jour de position pour les plateformes sans GPS."""
        self.lat += 0.0005
        self.lon += 0.001
        self.update_marker_and_center()
        if self.position_menu:
            self.position_menu.update_position(self.lat, self.lon)

    def update_marker_and_center(self):
        """Met à jour la position du marqueur et centre la carte."""
        if self.marker:
            self.remove_marker(self.marker)

        self.update_marker_icon()
        self.add_marker(self.marker)
        self.center_on(self.lat, self.lon)

    def update_marker_icon(self):
        """Update the marker icon depending on zoom level."""
        zoom = self.zoom  # Current zoom level
        
        # If zoom is less than a threshold, use a red point marker, otherwise use the wolf image
        if zoom < 12:
            self.marker = MapMarker(lat=self.lat, lon=self.lon)
            self.create_red_point_marker()
        else:
            self.marker = MapMarker(lat=self.lat, lon=self.lon, source="frontend/assets/wolf_icon.png")

    def create_red_point_marker(self):
        """Creates a red point marker for zoomed-out view."""
        # Red circle (1 cm max size) at the marker position
        with self.canvas:
            Color(1, 0, 0, 1)  # Red color
            self.red_point = Ellipse(pos=(self.lon, self.lat), size=(10, 10))  # Size can be adjusted as needed

        self.marker.add_widget(self.red_point)
