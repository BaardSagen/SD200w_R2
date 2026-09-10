import math

def salinity(C,T,P):
    if C<.01:return 0.
    R=C/42.914
    rt=.6766097+.0200564*T+.0001104259*T**2-6.9698e-7*T**3+1.0031e-9*T**4
    rp=1+P*(2.07e-5-6.37e-10*P+3.989e-15*P**2)/(1+.03426*T+.0004464*T*T+(.4215-.003107*T)*R)
    x=math.sqrt(abs(R/(rt*rp)));d=T-15
    return .008-.1692*x+25.3851*x*x+14.0941*x**3-7.0261*x**4+2.7081*x**5+d/(1+.0162*d)*(.0005-.0056*x-.0066*x*x-.0375*x**3+.0636*x**4-.0144*x**5)

import math

def sound_velocity(S,T,P):
    p=P/10
    D=.001727-7.9836e-6*p
    B=-.01922-4.42e-5*T+(7.3637e-5+1.7945e-7*T)*p
    A=1.389-.01262*T+7.164e-5*T*T+2.006e-6*T**3-3.21e-8*T**4
    A+=(9.4742e-5-1.258e-5*T-6.4885e-8*T*T+1.0507e-8*T**3-2.0122e-10*T**4)*p
    A+=(-3.9064e-7+9.1041e-9*T-1.6002e-10*T*T+7.988e-12*T**3)*p*p
    A+=(1.1e-10+6.649e-12*T-3.389e-13*T*T)*p**3
    W=1402.388+5.03711*T-.0580852*T*T+.0003342*T**3-1.478e-6*T**4+3.1464e-9*T**5
    W+=(.153563+.00068982*T-8.1788e-6*T*T+1.3621e-7*T**3-6.1185e-10*T**4)*p
    W+=(3.126e-5-1.7107e-6*T+2.5974e-8*T*T-2.5335e-10*T**3+1.0405e-12*T**4)*p*p
    W+=(-9.7729e-9+3.8504e-10*T-2.3643e-12*T*T)*p**3
    return W+A*S+B*math.sqrt(S**3)+D*S*S

import math

def density0(S,T):
    w=999.842594+.06793952*T-.00909529*T*T+.0001001685*T**3-1.120083e-6*T**4+6.536332e-9*T**5
    a=.824493-.0040899*T+7.6438e-5*T*T-8.2467e-7*T**3+5.3875e-9*T**4
    b=-.00572466+.00010227*T-1.6546e-6*T*T
    return w+a*S+b*math.sqrt(abs(S**3))+.00048314*S*S

def density_anomaly(S,T,P):
    p=P/10
    kw=19652.21+148.4206*T-2.327105*T*T+.01360477*T**3-5.155288e-5*T**4
    k0=kw+(54.6746-.603459*T+.0109987*T*T-6.167e-5*T**3)*S+(.07944+.016483*T-.00053009*T*T)*math.sqrt(abs(S**3))
    a=3.239908+.00143713*T+.000116092*T*T-5.77905e-7*T**3+(.0022838-1.0981e-5*T-1.6078e-6*T*T)*S+.000191075*math.sqrt(abs(S**3))
    b=8.50935e-5-6.12293e-6*T+5.2787e-8*T*T+(-9.9348e-7+2.0816e-8*T+9.1697e-10*T*T)*S
    K=k0+a*p+b*p*p
    return density0(S,T)/(1-p/K)-1000

def legacy_sigma(S,T):
    s=S-35
    q=28.1263+.806*s+.00023*s*s+6.8e-6*s**3
    a=(4.7867*T-.098185*T*T+.0010843*T**3)*.001
    b=(18.03*T-.8164*T*T+.01667*T**3)*1e-6
    w=-(T+283)*(T-3.98)**2/(503.57*(T+67.26))
    return (1-a+(q-.1324)*b)*(q+.1324)+w

import math

def gravity(latitude,P):
    x=math.sin(math.radians(latitude))**2
    return 9.780318*(1+(.0052788+2.36e-5*x)*x)+1.092e-6*P

def depth_unesco(latitude,P):
    return (((-1.82e-15*P+2.279e-10)*P-2.2512e-5)*P+9.72659)*P/gravity(latitude,P)

def oxygen_saturation_mg_l(S,T,air_mmHg):
    k=T+273.15
    a=math.exp(-139.34411+157570.1/k-66423080/k**2+12438000000/k**3-862194900000/k**4)
    b=math.exp(-S*(.017674-10.754/k+2140.7/k**2))
    theta=.000975-1.426e-5*T+6.436e-8*T*T
    vapor=math.exp(11.8571-3840.7/k-216961/k**2)
    p=air_mmHg*.00131578955679
    divisor=(1-vapor)*(1-theta)
    correction=(1-theta*p)*(p-vapor)/divisor if divisor else 1
    return a*b*correction

# Illustrative wrappers around the recovered core, not the complete SIT UI.
def temperature_from_resistance(R, a, b, c, d, old_kelvin=False):
    r = math.log(R)
    return 1/(a+b*r+c*r*r+d*r*r*r)-(273.16 if old_kelvin else 273.15)

def logger_depth(S, T, P, latitude=45.508368287):
    rho = 1000+density_anomaly(S,T,P)
    return 10000*P/(rho*gravity(latitude,P))

def oxygen_units(S, T, P, AP_hPa, percent):
    mg = oxygen_saturation_mg_l(S,T,AP_hPa*760/1013.25)*percent/100
    rho = 1000+density_anomaly(S,T,P)
    return (mg, mg*22.391/31.998, mg*1000/31.998,
            mg*22.391*1000/(716.467218*(rho/1000)))

# Two positive, increasing-pressure endpoints: illustration only.
def illustrative_layers(points, latitude=45.508368287):
    z = 0.0
    previous = 0.0
    for S,T,P in points:
        rho = 1000+density_anomaly(S,T,P)
        z += 10000*(P-previous)/(rho*gravity(latitude,P))
        previous = P
    return z

print(salinity(33.719632,7.773,16.72)) # 32.53899947
print(logger_depth(32.539,7.773,16.72)) # 16.62646309 m
print(sound_velocity(32.539,7.773,16.72)) # 1488.82737409 m/s
print(oxygen_units(32.539,7.773,16.72,925,3.47))
# mg/L, mL/L, umol/L, umol/kg (specified EOS-80 density convention)
print(illustrative_layers([(23.738,14.461,.30),(32.539,7.773,16.72)]))
# 16.62881923 m; not a whole-file Profiling result
