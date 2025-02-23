# frontend/utils/macos_gps.py
import CoreLocation
from kivy.clock import Clock

class MacOSGPS:
    def __init__(self, on_location=None):
        self.on_location = on_location
        self.location_manager = CoreLocation.CLLocationManager.alloc().init()
        self.location_manager.setDelegate_(self)
        self.auth_status = CoreLocation.CLLocationManager.authorizationStatus()
        print(f"[Init] Initial Authorization Status: {self.auth_status} (0=NotDetermined, 1=Restricted, 2=Denied, 3=WhenInUse, 4=Always)")
        
        if CoreLocation.CLLocationManager.locationServicesEnabled():
            print("[Init] Location Services are enabled system-wide")
            if self.auth_status == 0:  # NotDetermined
                print("[Init] Requesting location authorization...")
                self.location_manager.requestWhenInUseAuthorization()
            elif self.auth_status in (1, 2):
                print("[Init] Location access restricted or denied, please enable in System Settings")
            elif self.auth_status in (3, 4):
                print("[Init] Location access already granted")
        else:
            print("[Init] Location Services are disabled system-wide, please enable in System Settings")
        
        Clock.schedule_once(self.start_gps, 1)
        print(f"[Init] on_location set: {self.on_location is not None}")
        print(f"[Init] location_manager initialized: {self.location_manager is not None}")

    def start_gps(self, dt):
        """Start GPS updates."""
        self.auth_status = CoreLocation.CLLocationManager.authorizationStatus()
        print(f"[Start] Current Authorization Status: {self.auth_status}")
        if self.auth_status in (3, 4):  # AuthorizedWhenInUse or AuthorizedAlways
            print("MacOS GPS starting updates...")
            self.location_manager.startUpdatingLocation()
            Clock.schedule_interval(self.retry_get_location, 1)
        else:
            print(f"Cannot start GPS yet, auth status: {self.auth_status}")
            if self.auth_status == 0:  # Still waiting for user decision
                Clock.schedule_once(self.start_gps, 1)  # Retry

    def retry_get_location(self, dt):
        """Retry fetching location until successful."""
        loc = self.location_manager.location()
        if loc:
            coord = loc.coordinate()
            lat, lon = coord.latitude, coord.longitude
            print(f"Initial Location Retrieved - Lat: {lat}, Lon: {lon}")
            if self.on_location:
                self.on_location(lat=lat, lon=lon)
            return False  # Stop retrying
        print("Retry: No location data yet")

    def locationManager_didUpdateLocations_(self, manager, locations):
        """Handle GPS updates."""
        loc = locations.lastObject()
        if loc:
            coord = loc.coordinate()
            lat, lon = coord.latitude, coord.longitude
            print(f"Location Update - Lat: {lat}, Lon: {lon}")
            if self.on_location:
                self.on_location(lat=lat, lon=lon)
        else:
            print("Update received, but no valid location")

    def locationManager_didChangeAuthorizationStatus_(self, manager, status):
        """Handle authorization status changes."""
        self.auth_status = status
        print(f"[Auth Change] New Authorization Status: {status}")
        if status in (3, 4):
            self.start_gps(0)
        else:
            print(f"GPS disabled, auth status: {status}")