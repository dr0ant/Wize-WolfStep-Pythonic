from kivy.uix.widget import Widget
from kivy_garden.mapview import MapMarker
from kivy.graphics import Color, Line, Ellipse, PushMatrix, Rotate, PopMatrix, Triangle, Rectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.core.text import Label as CoreLabel

class UserMarker(Widget):
    opacity = NumericProperty(0.5)  # Base opacity for pulsing
    radar_scale = NumericProperty(0.1)  # Starts small and grows

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

    def draw_radar_effect(self):
        """Draw the radar pulse, arrow, and label with the correct layering."""
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

            # Draw the label "@dr0ant" above the wolf image
            core_label = CoreLabel(text="@dr0ant", font_size=32, color=(1, 1, 1, 1))  # White text
            core_label.refresh()  # Refresh to calculate texture size
            text_texture = core_label.texture

            # Position the text 20 pixels above the wolf image
            text_x = pixel_x - text_texture.width / 2  # Center horizontally
            text_y = pixel_y + self.wolf_marker.size[1] / 2 + 50  # 20 pixels above the wolf image

            # Add the text texture to the canvas
            self.canvas.add(Color(1, 1, 1, 1))  # Set the color to white
            self.canvas.add(Rectangle(texture=text_texture, pos=(text_x, text_y), size=(text_texture.width, text_texture.height)))

    def radar_pulse(self, dt):
        """Animate the radar pulse (expanding but NOT exceeding 400m)."""
        self.radar_scale += 0.03  # Gradually expand
        if self.radar_scale >= 1.0:  # When reaching 100% (400m), reset
            self.radar_scale = 0.1  # Restart from 10%
        self.canvas.clear()
        self.draw_radar_effect()