import time
import CoreLocation
from PyObjCTools import AppHelper

class MacOSGPS:
    def __init__(self, on_location=None):
        self.on_location = on_location
        self.location_manager = CoreLocation.CLLocationManager.alloc().init()
        self.location_manager.setDelegate_(self)
        self.location_manager.requestWhenInUseAuthorization()
        self.start_gps()

    def start_gps(self):
        """Start GPS updates."""
        self.location_manager.startUpdatingLocation()
        time.sleep(1)  # Allow time for location update
        self.get_location()

    def get_location(self):
        """Retrieve the latest location."""
        loc = self.location_manager.location()
        if loc:
            coord = loc.coordinate()
            lat, lon = coord.latitude, coord.longitude
            if self.on_location:
                self.on_location(lat=lat, lon=lon)

    def locationManager_didUpdateLocations_(self, manager, locations):
        """Handle GPS updates."""
        loc = locations.lastObject()
        if loc and self.on_location:
            lat, lon = loc.coordinate().latitude, loc.coordinate().longitude
            self.on_location(lat=lat, lon=lon)

# Ensure macOS event loop runs properly
if __name__ == "__main__":
    AppHelper.runConsoleEventLoop()
