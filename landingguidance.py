import krpc
import time
import math

g = 9.8

conn = krpc.connect('landingguidance')
print("Connected to server.")

vessel = conn.space_center.active_vessel
srf = vessel.orbit.body.reference_frame
trf = conn.space_center.target_vessel.reference_frame
brf = vessel.orbit.body.reference_frame
print("Connected to vessel '{0.name}'\n".format(vessel))

################################################################################

def dotProduct(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def crossProduct(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

def magnitude(x):
    return math.sqrt(dotProduct(x, x))

def add(a, b):
    return (a[0] + b[0],
            a[1] + b[1],
            a[2] + b[2])

def subtract(a, b):
    return (a[0] - b[0],
            a[1] - b[1],
            a[2] - b[2])

def scale(a, b):
    return (a[0]*b,
            a[1]*b,
            a[2]*b)

def unitVector(x):
    return scale(x, 1/magnitude(x))

def oppositeVector(x):
    return scale(x, -1)

################################################################################

def twr(vessel):
    return (vessel.available_thrust)/(vessel.mass*g)

def twrToThrottle(vessel, setting):
    vessel.control.throttle = (setting/twr(vessel))

def correctHdgBallistic(vessel):
    target_rf = trf
    velVector = vessel.flight(srf).prograde
    tgtVector = vessel.position(target_rf)
    vessel.auto_pilot.target_direction = conn.space_center.transform_position(add(tgtVector, scale(velVector, 1/8)), trf, brf)
    conn.drawing.add_direction(add(tgtVector, scale(velVector, 1/8)), brf)

def correctHdgPowered(vessel):
    target_rf = trf
    velVector = vessel.flight(target_rf).prograde
    tgtVector = vessel.position(target_rf)
    vessel.auto_pilot.target_direction = conn.space_center.transform_position(subtract(tgtVector, scale(velVector, 1/4)), trf, brf)
    conn.drawing.add_direction(subtract(tgtVector, scale(velVector, 1/4)), brf)

################################################################################

pause = input("Press enter to initiate landing.")
del pause

print("Cruising till descent burn.")
vessel.auto_pilot.engage()
vessel.auto_pilot.reference_frame = brf
vessel.auto_pilot.auto_tune = False
vessel.auto_pilot.roll_pid_gain = (0, 0, 0)
while vessel.flight(srf).surface_altitude > 40000:
    vessel.auto_pilot.target_direction = vessel.flight(srf).retrograde
    conn.drawing.add_direction(unitVector(vessel.flight(srf).retrograde), srf)
    time.sleep(0.2)

print("Descent burn started.")
vessel.control.throttle = 1
while vessel.flight(srf).speed > 750:
    correctHdgPowered(vessel)
    time.sleep(0.1)
vessel.control.throttle = 0

print("Waiting for suicide burn altitude.")
burnStarted = False
target_alt = 12
while abs(vessel.flight(srf).vertical_speed) > 4:
    alt = vessel.flight(srf).surface_altitude
    vel = abs(vessel.flight(srf).vertical_speed)
    dist = abs(target_alt - alt) #/math.tan(90 - abs(vessel.flight(srf).pitch()))
    req_acc = (vel*vel)/(2*dist)
    req_twr = 1 + (req_acc/g)
    if burnStarted == False:
        if req_twr < 4.0 and req_twr < twr(vessel):
            correctHdgBallistic(vessel)
            time.sleep(0.2)
            continue
        burnStarted = True
        print("Landing burn started.")
    if alt > 500:
        correctHdgPowered(vessel)
    else:
        vessel.auto_pilot.target_direction = unitVector(vessel.flight(srf).retrograde)
    twrToThrottle(vessel, req_twr)
    print(str(round(alt, 1)) + ",", str(round(vessel.control.throttle*100, 1)),
          "({0}/{1})".format(str(round(req_twr, 1)), str(round(twr(vessel), 1))))

for leg in vessel.parts.legs:
    if leg.is_grounded == True:
        break
    else:
        twrToThrottle(vessel, 1.0 + 0.01*vessel.flight(srf).vertical_speed)
    time.sleep(0.1)

vessel.control.throttle = 0
vessel.auto_pilot.disengage()
print("Shutdown!")

pause = input("Press enter to exit.")
del pause
