# frontend/markers/user_marker.py
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapMarker
from kivy.graphics import Color, Ellipse, Line, PushMatrix, Rotate, PopMatrix, Rectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window  # Added back the missing import

class UserMarker(Widget):
    opacity = NumericProperty(0.5)  # Base opacity for pulsing
    radar_scale = NumericProperty(0.1)  # Starts small and grows
    is_hovered = BooleanProperty(False)  # Track hover state
    info_popup = ObjectProperty(None, allownone=True)  # Popup widget

    def __init__(self, map_view, lat, lon, **kwargs):
        super().__init__(**kwargs)
        self.map_view = map_view
        self.lat = lat
        self.lon = lon
        self.direction = 0  # Default direction (0° = north)

        # Start radar animation
        Clock.schedule_interval(self.radar_pulse, 0.05)

        # Wolf icon (on top)
        self.wolf_marker = MapMarker(lat=self.lat, lon=self.lon, source="frontend/assets/wolf_icon.png")
        self.wolf_marker.size = (128, 128)  # Initial size
        self.map_view.add_marker(self.wolf_marker)

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
        self.wolf_marker = MapMarker(lat=self.lat, lon=self.lon, source="frontend/assets/wolf_icon.png")
        self.wolf_marker.size = (32, 32)  # Adjusted size for updates
        self.map_view.add_marker(self.wolf_marker)

        # Update popup position if it exists
        if self.info_popup:
            self.update_popup_position()

    def draw_radar_effect(self):
        """Draw the radar pulse and arrow without a fixed border."""
        with self.canvas:
            # Convert lat/lon to pixel coordinates
            pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)

            # Calculate 200m radius in pixels
            meters_per_pixel = 156543.03392 * (2 ** (-self.map_view.zoom))
            max_radius_pixels = 200 / meters_per_pixel  # Fixed 200m limit

            # Pulsing radar effect (expanding circle)
            pulse_radius = self.radar_scale * max_radius_pixels  # Scales from 10% to 100%
            Color(1, 0, 0, max(0, 0.5 - self.radar_scale * 0.5))  # Red fade-out effect
            Ellipse(pos=(pixel_x - pulse_radius, pixel_y - pulse_radius), 
                    size=(pulse_radius * 2, pulse_radius * 2))

            # Green arrow indicating direction
            Color(0, 1, 0, 1)  # Solid green
            PushMatrix()
            Rotate(angle=-self.direction, origin=(pixel_x, pixel_y))
            Line(points=[pixel_x, pixel_y, pixel_x, pixel_y + 30], width=3)  # Shaft
            Line(points=[pixel_x - 8, pixel_y + 25, pixel_x, pixel_y + 30], width=3)  # Left wing
            Line(points=[pixel_x + 8, pixel_y + 25, pixel_x, pixel_y + 30], width=3)  # Right wing
            PopMatrix()

            # Hover border (drawn last to be under wolf but over circle)
            if self.is_hovered:
                Color(0, 1, 0, 1)  # Green border
                Line(rectangle=(pixel_x - 16, pixel_y - 16, 32, 32), width=2)  # Around 32x32 wolf

    def radar_pulse(self, dt):
        """Animate the radar pulse (expanding but NOT exceeding 200m)."""
        self.radar_scale += 0.03  # Gradually expand
        if self.radar_scale >= 1.0:  # When reaching 100% (200m), reset
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
        """Create and show the info popup centered at the radar radius."""
        # Hardcoded user info (replace with MongoDB later)
        user_info_text = "Name: John Doe\nAge: 30\nLocation: New York, USA\nBio: Software Developer passionate about data science and machine learning."

        # Create the label for user info
        info_label = Label(
            text=user_info_text,
            font_size='14sp',
            size_hint=(None, None),
            size=(200, 100),
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )
        info_label.bind(size=info_label.setter('text_size'))  # Wrap text

        # Create a BoxLayout with background color
        bubble_layout = BoxLayout(orientation='vertical', size=(200, 100))
        with bubble_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = Rectangle(pos=bubble_layout.pos, size=bubble_layout.size)
        bubble_layout.bind(pos=self.update_bg_rect, size=self.update_bg_rect)
        bubble_layout.add_widget(info_label)

        # Position centered at wolf (same as radar)
        pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)
        window_x = pixel_x - 100  # Center horizontally (200/2)
        window_y = pixel_y - 50   # Center vertically (100/2)

        # Create the popup widget as a child of UserMarker
        self.info_popup = Widget(size=(200, 100), pos=(window_x, window_y))
        self.info_popup.add_widget(bubble_layout)
        self.add_widget(self.info_popup)

        # Debug positioning
        print(f"Wolf at: ({pixel_x}, {pixel_y}), Popup at: ({window_x}, {window_y})")

    def update_bg_rect(self, instance, value):
        """Update the background rectangle position and size."""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

    def update_popup_position(self):
        """Update the popup position to match the radar center."""
        if self.info_popup:
            pixel_x, pixel_y = self.map_view.get_window_xy_from(self.lat, self.lon, self.map_view.zoom)
            window_x = pixel_x - 100  # Center horizontally (200/2)
            window_y = pixel_y - 50   # Center vertically (100/2)
            self.info_popup.pos = (window_x, window_y)
            print(f"Popup updated to: ({window_x}, {window_y})")

    def remove_info_popup(self):
        """Remove the info popup from UserMarker."""
        if self.info_popup:
            self.remove_widget(self.info_popup)
            self.info_popup = None