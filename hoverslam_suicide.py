from math import log as ln

g = 9.8

def stoppingDist(vessel, max_g):
    mass = vessel.mass
    dry_mass = vessel.dry_mass
    isp = vessel.specific_impulse
    thrust = mass*g*max_g if mass*g*max_g < vessel.available_thrust else vessel.available_thrust
    v = abs(vessel.flight(vessel.orbit.body.reference_frame).vertical_speed)

    upper_lim = (mass - dry_mass)*(isp*g)/thrust #Burn time
    lower_lim = 0
    t = 0
    dv = 0
    max_cycles = 20

    while abs(v - dv) > 1 and max_cycles:
        t = (upper_lim + lower_lim)/2
        dv = -g*(isp*ln(1 - (thrust*t)/(mass*isp*g)) + t) #dv in time t
        if dv > v:
            upper_lim = t
        else:
            lower_lim = t
        max_cycles -= 1
    '''
    return -g*(2*isp*(thrust*t - mass*isp*g)*ln(1 - (thrust*t)/(mass*isp*g))
               + thrust*t*(t - 2*isp))/(2*thrust) #s in time t
    '''
    r = thrust/(isp*g)
    return (thrust/r)*(t*ln(mass) + ((mass - r*t)*(ln(mass - r*t) - 1) - mass*(ln(mass) - 1))/r) - (1/2)*g*t**2

if __name__ == '__main__':
    class vessel:
        class flight:
            def __init__(self, ref):
                self.vertical_speed = 400
        class orbit:
            class body:
                reference_frame = 0
        def __init__(self, mass, dry_mass, isp, available_thrust):
            self.mass = mass
            self.dry_mass = dry_mass
            self.specific_impulse = isp
            self.available_thrust = available_thrust

    print(stoppingDist(vessel(32000, 20000, 300, 3500000), 4))
