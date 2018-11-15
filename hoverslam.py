import krpc
import time
import math

g = 9.8

conn = krpc.connect('hoverslam')
print("Connected to server.")

vessel = conn.space_center.active_vessel
srf = vessel.orbit.body.reference_frame
print("Connected to vessel '{0.name}'\n".format(vessel))

def twr(vessel):
    return (vessel.available_thrust)/(vessel.mass*g)

def twrToThrottle(vessel, setting):
    vessel.control.throttle = (setting/twr(vessel))

pause = input("Press enter to initiate landing.")
del pause

print("Waiting for landing burn start.")
burnStarted = False
target_alt = 15
while vessel.flight(srf).speed > 5:
    alt = vessel.flight(vessel.orbit.body.reference_frame).surface_altitude
    vel = vessel.flight(vessel.orbit.body.reference_frame).speed
    dist = abs(target_alt - alt)
    req_acc = (vel*vel)/(2*dist)
    req_twr = 1 + (req_acc/g)
    if burnStarted == False:
        if req_twr < 4.0 and req_twr < twr(vessel):
            continue
        burnStarted = True
        print("Landing burn started.")
        print("Throttle setting:")
    twrToThrottle(vessel, req_twr)
    print(round(vessel.control.throttle*100, 1))
    time.sleep(0.1)

vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch = 90
for leg in vessel.parts.legs:
    if leg.is_grounded == True:
        break
    else:
        twrToThrottle(vessel, 1.05)
    time.sleep(0.1)

vessel.control.throttle = 0
vessel.auto_pilot.disengage()
print("Shutdown!")

pause = input("Press enter to exit.")
del pause
