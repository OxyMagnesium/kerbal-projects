import krpc
import time
import math

g = 9.8

conn = krpc.connect('kerbalhopper')
print("Connected to server.")

vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot
control = vessel.control
print("Connected to vessel '{0.name}'\n".format(vessel))

srf = vessel.orbit.body.reference_frame

def twr(vessel):
    return (vessel.available_thrust)/(vessel.mass*g)

def twrToThrottle(vessel, setting):
    vessel.control.throttle = (setting/twr(vessel))

def stoppingDist(vel, acc):
    return (vel*vel)/(2*acc)

def stoppingDistMaintain(vessel, target_alt):
    alt = vessel.flight(vessel.orbit.body.reference_frame).surface_altitude
    vel = vessel.flight(vessel.orbit.body.reference_frame).speed
    dist = abs(target_alt - alt)

    req_acc = (vel*vel)/(2*dist)
    if target_alt > alt:
        req_twr = 1 - (req_acc/g)
    else:
        req_twr = 1 + (req_acc/g)

    twrToThrottle(vessel, req_twr)

pause = input("Continue?\n")
del pause

#Pre-launch
ap.engage()
ap.target_pitch_and_heading(90, 90)
control.throttle = 1
print("Pre-launch complete.")

time.sleep(1)

#Liftoff
control.activate_next_stage()
print("Liftoff!")

time.sleep(1)

#Wait until braking start
target_alt = 500
print("Waiting for braking start.")
while stoppingDist(vessel.flight(srf).speed, 0.25*g) < abs(target_alt - vessel.flight(srf).surface_altitude):
    time.sleep(0.1)

#Start braking
print("Braking started.")
while vessel.flight(srf).speed > 0.5:
    stoppingDistMaintain(vessel, target_alt)
    time.sleep(0.1)

#Maintain target alt
timeStart = time.time()
print("Maintaining altitude.")
while time.time() - timeStart < 15.0:
    twrToThrottle(vessel, 1.0)
    time.sleep(0.1)

#Start descent
print("Starting descent.")
twrToThrottle(vessel, 0.5)
time.sleep(1)

#Wait until landing burn start
target_alt = 20
print("Waiting for braking start. ")
while stoppingDist(vessel.flight(srf).speed, 0.5*g*twr(vessel) - g) < abs(target_alt - vessel.flight(srf).surface_altitude):
    twrToThrottle(vessel, 0.75)
    time.sleep(0.1)

#Start landing
print("Braking started.")
while vessel.flight(srf).speed > 5:
    stoppingDistMaintain(vessel, target_alt)
    time.sleep(0.1)
while vessel.flight(srf).speed > 0.5:
    twrToThrottle(vessel, 1.05)
    time.sleep(0.1)

#Shutdown
control.throttle = 0
ap.disengage()
print("Shutdown.")
pause = input("Press enter to exit.")
del pause
