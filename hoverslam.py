import krpc
import time
import math
from hoverslam_suicide import stoppingDist

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

def printTelemetry(vessel):
    buffer = '{0} m; {1} m/s; {2}%'.format(round(vessel.flight(srf).surface_altitude),
                                           round(vessel.flight(srf).vertical_speed),
                                           round(vessel.control.throttle, 1)*100)
    print(buffer)

input("Press enter to initiate landing.")

print("Waiting for landing burn start.")
max_g = 4
target_alt = 15
while vessel.flight(srf).surface_altitude - 1.1*stoppingDist(vessel, max_g) > 0:
    printTelemetry(vessel)
    print(stoppingDist(vessel, max_g))

print("Landing burn started.")
while abs(vessel.flight(srf).vertical_speed) > 1:
    alt = vessel.flight(srf).surface_altitude
    vel = vessel.flight(srf).vertical_speed
    dist = abs(target_alt - alt)*0.75 #/math.cos(math.radians(abs(90 - vessel.flight(srf).pitch)))
    req_acc = (vel*vel)/(2*dist)
    req_twr = 1 + (req_acc/g)
    printTelemetry(vessel)
    if req_twr > max_g:
        req_twr = max_g
    try:
        twrToThrottle(vessel, req_twr)
    except ZeroDivisionError:
        break

#for leg in vessel.parts.legs:
while True:
    if abs(vessel.flight(srf).vertical_speed) < 1: #or leg.is_grounded == True:
        for i in range(0, 100):
            vessel.control.throttle -= 1
            time.sleep(0.05)
        break
    else:
        try:
            twrToThrottle(vessel, 1.0)
        except ZeroDivisionError:
            print('Out of propellant!')
            break

vessel.control.throttle = 0
print("Shutdown!")
