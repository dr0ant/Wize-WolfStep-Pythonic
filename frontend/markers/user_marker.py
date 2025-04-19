# frontend/markers/user_marker.py
from kivy.uix.widget import Widget
from kivy_garden.mapview import MapMarker
from kivy.graphics import Color, Ellipse, Line, PushMatrix, Rotate, PopMatrix, Triangle
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.window import Window
from frontend.markers.user_popup import UserPopup

class UserMarker(Widget):
    opacity = NumericProperty(0.5)  # Base opacity for pulsing
    radar_scale = NumericProperty(0.1)  # Starts small and grows
    is_hovered = BooleanProperty(False)  # Track hover state

    def __init__(self, map_view, lat, lon, **kwargs):
        super().__init__(**kwargs)
        self.map_view = map_view
        self.lat = lat
        self.lon = lon
        self.direction = 0  # Default direction (0° = north)

        # Start radar animation
        Clock.schedule_interval(self.radar_pulse, 0.05)

        # Wolf icon (on top)
        self.wolf_marker = MapMarker(lat=self.lat, lon=self.lon, source="frontend/assets/wolf_no_BG.png")
        self.wolf_marker.size = (128, 128)  # Initial size
        self.map_view.add_marker(self.wolf_marker)

        # Initialize popup reference
        self.info_popup = None

        # Bind map touch events for click and hover
        self.map_view.bind(on_touch_down=self.on_map_touch_down)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def update_position(self, lat, lon, direction=0):
        """Update marker position and direction."""
        self.lat = lat
        self.lon = lon
        self.direction = direction

        self.canvas.clear()
        self.draw_radar_effect()

        # Update wolf marker position (on top)
        self.map_view.remove_marker(self.wolf_marker)
        self.wolf_marker = MapMarker(lat=self.lat, lon=self.lon, source="frontend/assets/wolf_no_BG.png")
        self.wolf_marker.size = (128, 128)  # Adjusted size for updates
        self.map_view.add_marker(self.wolf_marker)

        # Update popup position if it exists
        if self.info_popup:
            self.info_popup.update_position()

    def draw_radar_effect(self):
        """Draw the radar pulse and arrow with the correct layering."""
        with self.canvas:
            # Convert lat/lon to pixel coordinates
            pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)

            # Calculate 400m radius in pixels
            meters_per_pixel = 156543.03392 * (2 ** (-self.map_view.zoom))
            max_radius_pixels = 400 / meters_per_pixel  # Fixed 400m limit

            # Pulsing radar effect (expanding circle)
            pulse_radius = self.radar_scale * max_radius_pixels  # Scales from 10% to 100%
            Color(1, 0, 0, max(0, 0.5 - self.radar_scale * 0.5))  # Red fade-out effect
            Ellipse(pos=(pixel_x - pulse_radius, pixel_y - pulse_radius), 
                    size=(pulse_radius * 2, pulse_radius * 2))

            # Light red arrow indicating direction
            Color(1, 0.5, 0.5, 1)  # Light red for the arrowhead
            PushMatrix()
            Rotate(angle=-self.direction, origin=(pixel_x, pixel_y))
            # Draw arrowhead as a triangle
            Triangle(
                points=[
                    pixel_x, pixel_y + 30,     # Arrow tip (north)
                    pixel_x - 10, pixel_y + 10, # Left side
                    pixel_x + 10, pixel_y + 10  # Right side
                ]
            )
            # Very light gray tail spikes
            Color(0.9, 0.9, 0.9, 1)  # Very light gray for the tail spikes
            Line(points=[pixel_x - 10, pixel_y - 10, pixel_x, pixel_y - 20], width=3)  # Left spike
            Line(points=[pixel_x + 10, pixel_y - 10, pixel_x, pixel_y - 20], width=3)  # Right spike
            PopMatrix()

            # Hover border (drawn last to be under wolf but over circle)
            if self.is_hovered:
                Color(1, 1, 1, 1)  # Solid white
                Line(rectangle=(pixel_x - 0, pixel_y - 0, 128, 128), width=2)  # Border around the wolf icon

        # Ensure the wolf_marker is always on top
        self.map_view.remove_marker(self.wolf_marker)
        self.map_view.add_marker(self.wolf_marker)

    def on_mouse_pos(self, window, pos):
        """Detect hover by checking mouse position relative to marker."""
        pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)
        marker_size = self.wolf_marker.size

        # Adjust hover detection to better match the icon's shape
        hover_margin_x = 20  # Adjust this value to better match the icon's width
        hover_margin_y = 40  # Adjust this value to better match the icon's height
        adjusted_bounds = (
            pixel_x - hover_margin_x,
            pixel_y - hover_margin_y,
            pixel_x + hover_margin_x,
            pixel_y + hover_margin_y
        )

        if (adjusted_bounds[0] <= pos[0] <= adjusted_bounds[2] and 
            adjusted_bounds[1] <= pos[1] <= adjusted_bounds[3]):
            if not self.is_hovered:
                self.is_hovered = True
                self.canvas.clear()
                self.draw_radar_effect()
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.canvas.clear()
                self.draw_radar_effect()
 

    def radar_pulse(self, dt):
        """Animate the radar pulse (expanding but NOT exceeding 400m)."""
        self.radar_scale += 0.03  # Gradually expand
        if self.radar_scale >= 1.0:  # When reaching 100% (400m), reset
            self.radar_scale = 0.1  # Restart from 10%
        self.canvas.clear()
        self.draw_radar_effect()

    def on_map_touch_down(self, instance, touch):
        """Handle clicks on the map to detect marker interaction."""
        pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)
        marker_size = self.wolf_marker.size  # (32, 32)
        marker_bounds = (
            pixel_x - marker_size[0] / 2,
            pixel_y - marker_size[1] / 2,
            pixel_x + marker_size[0] / 2,
            pixel_y + marker_size[1] / 2
        )

        if (marker_bounds[0] <= touch.x <= marker_bounds[2] and 
            marker_bounds[1] <= touch.y <= marker_bounds[3]):
            print("Marker clicked!")
            self.toggle_info_popup()
            return True  # Consume the touch event
        return False

    def on_mouse_pos(self, window, pos):
        """Detect hover by checking mouse position relative to marker."""
        pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)
        marker_size = self.wolf_marker.size
        marker_bounds = (
            pixel_x - marker_size[0] / 2,
            pixel_y - marker_size[1] / 2,
            pixel_x + marker_size[0] / 2,
            pixel_y + marker_size[1] / 2
        )

        if (marker_bounds[0] <= pos[0] <= marker_bounds[2] and 
            marker_bounds[1] <= pos[1] <= marker_bounds[3]):
            if not self.is_hovered:
                self.is_hovered = True
                self.canvas.clear()
                self.draw_radar_effect()
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.canvas.clear()
                self.draw_radar_effect()

    def toggle_info_popup(self):
        """Toggle the info popup visibility."""
        if self.info_popup:
            self.remove_info_popup()
        else:
            self.show_info_popup()

    def show_info_popup(self):
        """Show the info popup 10px above the UserMarker using Kivy Popup."""
        self.info_popup = UserPopup(self)
        self.info_popup.open()

    def remove_info_popup(self):
        """Dismiss the info popup."""
        if self.info_popup:
            self.info_popup.dismiss()
            self.info_popup = None