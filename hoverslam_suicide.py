from math import log

def stoppingDist(vessel, max_g):
    mass = vessel.mass
    dry_mass = vessel.dry_mass
    isp = vessel.specific_impulse
    thrust = mass*g*max_g if mass*g*max_g < vessel.available_thrust else vessel.available_thrust
    v = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed

    upper_lim = (mass - dry_mass)*(isp*g)/thrust
    lower_lim = 0
    t = 0
    dv = 0
    max_cycles = 20

    while abs(v - dv) > 1 and max_cycles > 0:
        t = (upper_lim + lower_lim)/2
        dv = -g*(isp*log(1 - (thrust*t)/(mass*isp*g)) + t)
        if dv > v:
            upper_lim = t
        else:
            lower_lim = t
        max_cycles -= 1

    return -g*(2*isp*(thrust*t - mass*isp*g)*log(1 - (thrust*t)/(mass*isp*g))
               + thrust*t*(t - 2*isp))/(2*thrust)
