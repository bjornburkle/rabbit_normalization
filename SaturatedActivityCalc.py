import os, sys
import pandas as pd
import numpy as np
import math

def calcInitAct(act, wt, hl):
    '''
    Takes the measured activity from gamma spectroscopy, and uses information about
    isotope lifetime and the amount of time between end of irradiation and gamma spec
    measurement to calculate what the activity would have been when the irradiation ended

    Inputs are:
        -act -- activity measured from gamma spectroscopy
        -wt -- the amount of time in hours between the irradiation ending and gamma spec measurement
        -hl -- the halflife in units of hours, gets converted to decay constant in function
    '''

    decay = math.log(2)/hl
    iact = act*math.exp(wt * decay)
    return iact

def calcSatAct(act, it, hl, nm, mass, frac):
    '''
    Uses the activity at the end of irradiation, isotope decay constant, and irradiation 
    to calculate the acitivty at saturation.

    Activity at saturation is then converted from units to uCi to nuclear decay per nuclean to second
    which acts as a normalized unit

    Inputs are:
        -act -- activity at end of irraidation
        -it -- amount of time in hours that foil was irradiated for
        -lf -- the daugter isotope halflife in hours, gets converted to decay constant in function
        -nm -- the nuclear mass (number of protons + neutrons) of daughter isotope
        -mass -- mass of the foil
        -frac -- the fraction of natural occuring element that is the type of the activated isotope
    '''

    decay = math.log(2)/hl
    sact = act / (1 - math.exp(-it * decay) )
    sact = 3.7e4 * sact * nm / (mass * 6.02e23 * frac)
    # 3.7e4 is a conversion unit from uCi to decays per second
    return sact

if __name__ == '__main__':
    pass
