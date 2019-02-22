from math import log

g = 9.8
isp = 300
mass = 30000
dry_mass = 20000
thrust = 750000
t = 0

def suicideDeltaV(t):
    return -g*(isp*log(1 - (thrust*t)/(mass*isp*g)) + t)

def velocityKillTime(v):
    upper_lim = (mass - dry_mass)*(isp*g)/thrust
    lower_lim = 0
    t = 0
    dv = 0
    max_cycles = 10

    while abs(v - dv) > 1 and max_cycles > 0:
        t = (upper_lim + lower_lim)/2
        dv = suicideDeltaV(t)
        print(dv, t)
        if dv > v:
            upper_lim = t
        else:
            lower_lim = t
        max_cycles -= 1

    return t

def stoppingDist(v):
    t = velocityKillTime(v)
    return -g*(2*isp*(thrust*t - mass*isp*g)*log(1 - (thrust*t)/(mass*isp*g))
               + thrust*t*(t - 2*isp))/(2*thrust)

speed = input()
if speed == "":
    speed = 250
else:
    speed = int(speed)
print(stoppingDist(speed))
