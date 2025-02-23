from CoreLocation import CLLocationManager
import time

manager = CLLocationManager.alloc().init()
manager.requestWhenInUseAuthorization()

# Keep script running so you can check system prompts
while True:
    time.sleep(1)
