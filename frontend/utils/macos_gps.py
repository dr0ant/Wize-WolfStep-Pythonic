import geocoder
from kivy.clock import Clock

class MacOSGPS:
    def __init__(self, on_location=None):
        """
        Initialize the GPS class and fetch the location using geocoder.
        """
        self.on_location = on_location
        self.auth_status = None  # Simulate authorization status
        print("[Init] Initializing MacOSGPS...")
        Clock.schedule_once(self.check_authorization, 0)

    def check_authorization(self, dt):
        """
        Simulate checking authorization for location services.
        """
        print("[Auth] Checking location authorization...")
        # Simulate authorization status (always authorized for geocoder)
        self.auth_status = 3  # AuthorizedWhenInUse
        if self.auth_status in (3, 4):  # AuthorizedWhenInUse or AuthorizedAlways
            print("[Auth] Location access granted")
            self.start_gps(0)
        else:
            print("[Auth] Location access denied")

    def start_gps(self, dt):
        """
        Start fetching GPS updates using geocoder.
        """
        print("[Start] Starting GPS updates...")
        Clock.schedule_once(self.fetch_location, 0)

    def fetch_location(self, dt):
        """
        Fetch the current location using geocoder and call the callback.
        """
        print("[Fetch] Fetching location using geocoder...")
        try:
            location = geocoder.ip('me').latlng
            print(f"[Debug] Geocoder returned: {location}")
            if location:
                lat, lon = location
                print(f"[Fetch] Location fetched successfully - Lat: {lat}, Lon: {lon}")
                if self.on_location:
                    self.on_location(lat=lat, lon=lon)
            else:
                print("[Fetch] Unable to fetch location. Please check your internet connection.")
        except Exception as e:
            print(f"[Fetch] Error fetching location: {e}")

    def locationManagerDidChangeAuthorization_(self, manager):
        """
        Simulate handling authorization status changes (modern macOS).
        """
        print("[Auth Change] Authorization status changed")
        self.check_authorization(0)

    def locationManager_didChangeAuthorizationStatus_(self, manager, status):
        """
        Simulate handling authorization status changes (legacy macOS).
        """
        print(f"[Auth Change] New Authorization Status (legacy): {status}")
        self.auth_status = status
        if status in (3, 4):  # AuthorizedWhenInUse or AuthorizedAlways
            self.start_gps(0)
        else:
            print("[Auth Change] GPS disabled, auth status: {status}")

    def locationManager_didUpdateLocations_(self, manager, locations):
        """
        Simulate handling GPS updates.
        """
        print("[Update] Simulating GPS updates...")
        self.fetch_location(0)


if __name__ == "__main__":
    def test_on_location(lat, lon):
        print(f"[Test] Callback received - Lat: {lat}, Lon: {lon}")
        return lat, lon

    print("[Test] Initializing MacOSGPS for testing...")
    gps = MacOSGPS(on_location=test_on_location)
    gps.fetch_location(0)  # Appel direct pour tester