# frontend/markers/user_popup.py
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Triangle

class UserPopup(Popup):
    def __init__(self, user_marker, **kwargs):
        super().__init__(**kwargs)
        self.user_marker = user_marker  # Reference to UserMarker for positioning
        self.size_hint = (0.15, 0.15/2)  # Disable size hint to enforce fixed size
        #self.size = (200, 200)  # Fixed size from previous update
        self.auto_dismiss = False  # Manual dismiss with close button
        self.background = ''  # Remove gray overlay background


        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', spacing=2)

        # Hardcoded user info
        user_info_text = "@dr0ant"

        # Create the label for user info
        info_label = Label(
            text=user_info_text,
            font_size='16sp',
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            size_hint_y=80  # Adjusted to fit with close button
        )
        info_label.bind(size=info_label.setter('text_size'))  # Wrap text

        # Close button
        close_button = Button(
            text='X',
            size_hint=(None, None),
            size=(30, 30),
            font_size='20sp',
            background_color=(1, 0, 0, 1),  # Red background
            color=(1, 1, 1, 1),  # White text
            pos_hint={'right': 1, 'top': 1}
        )
        close_button.bind(on_release=self.dismiss)

        # Content layout (info + close button)
        content_layout = BoxLayout(orientation='vertical', size=self.size)
        with content_layout.canvas.before:
            # Leaflet tail (triangle at bottom, no background rectangle)
            Color(1, 1, 1, 1)  # White tail
            self.tail = Triangle(points=[
                content_layout.center_x - 10, content_layout.y,  # Left
                content_layout.center_x + 10, content_layout.y,  # Right
                content_layout.center_x, content_layout.y - 15   # Bottom tip
            ])
        content_layout.bind(pos=self.update_tail_position)
        content_layout.add_widget(info_label)
        content_layout.add_widget(close_button)

        # Set the content of the popup
        self.content = content_layout

        # Position 1cm above the UserMarker
        self.update_position()

    def update_tail_position(self, instance, value):
        """Update the tail position."""
        self.tail.points = [
            instance.center_x - 10, instance.y,  # Left
            instance.center_x + 10, instance.y,  # Right
            instance.center_x, instance.y - 15   # Bottom tip
        ]

    def update_position(self):
        """Update the popup position to 1cm (38px) above the UserMarker."""
        if self.user_marker:
            pixel_x, pixel_y = self.user_marker.map_view.get_window_xy_from(
                self.user_marker.lat, self.user_marker.lon, self.user_marker.map_view.zoom
            )
            marker_height = self.user_marker.wolf_marker.size[1]  # Wolf height (32px)
            # Position 1cm (38px) above the wolf marker, centered horizontally
            window_x = pixel_x - (self.width / 2)  # Center horizontally
            window_y = pixel_y + marker_height + 38  # 1cm (38px) above wolf top
            self.pos = (window_x, window_y)
            print(f"Popup positioned at: ({window_x}, {window_y}), Size: {self.size}")