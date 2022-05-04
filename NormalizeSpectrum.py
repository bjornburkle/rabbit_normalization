import os, sys
import numpy as np
import pandas as pd

def getXsec(inDir, isotopes):
    '''
    Obtain the necessary activation cross sections for the mother isotopes
    as well as the energy binning. Default is for inDir to be the
    "inputs" directory
    '''
    # need to read the "energy" file to obtain the xsec energy binning
    isotopes.append('energy')
    xsec = {}
    for iso in isotopes:
        f = open('%s/%s.txt' % (inDir, iso), 'r').readlines()
        xsec[iso] = np.array([float(val) for line in f for val in line.split()])

    return xsec

def getDamage(filename):
    '''
    Read the si damage function and its energy binning from
    one of the input files and return a dict.
    Works similarly to the getXsec() function, but the damage function
    file format is slightly different, so requires a different parsing method.
    '''

    damage = {
        'damage': [],
        'energy': []
    }
    f = open(filename, 'r').readlines()
    for line in f:
        damage['energy'].append(float(line.split(',')[0]))
        damage['damage'].append(float(line.split(',')[1]))

    damage['energy'].append(20)
    damage['energy'] = np.array(damage['energy'])
    damage['damage'] = np.array(damage['damage'])

    return damage

def calcAct(spectrum, xsec, energy):
    #s_vec = spectrum.vectorize(energy)
    act = spectrum[:-1]*xsec*(energy[1:]-energy[:-1])
    #print(act)
    #print(np.sum(act))
    return np.sum(act)

def readSpectrum(filename):
    '''
    Function parses the neutron energy spectrum output files produced from the
    script used to derive the original neutron spectrums.
    From those files it extracts the normalization for the thermal,
    intermediate, and fission neutron spectrums, as well as the energy
    values where the spectrum changes from one type of functional description
    to another.
    '''

    # This was more or less taken from the old version of the script, so it's a bit more jank
    f = open(filename, 'r').readlines()
    pars = [0, 0, 0]
    cons = [0, 0]
    nextline = False
    for line in f:
        if 'Thermal Scale' in line:
            pars[0] = float(line.split(':\t')[-1])
        if 'Interm Scale' in line:
            pars[1] = float(line.split(':\t')[-1])
        if 'Fission Scale' in line:
            pars[2] = float(line.split(':\t')[-1])
        if nextline:
            cons[0] = float(line.split(',\t')[0])
            cons[1] = float(line.split(',\t')[1])
            nextline = False
        if 'Connection' in line:
            nextline = True

    return pars, cons


def makeSpectrum(x, pars, con):
    '''
    Takes the set of normalizations for the suspected piecewise neutron energy
    spectrum and calculates the resulting energy spectrum for a given energy binning (x)
    '''

    kT = 3.93E7 # temperature of the reactor water (around 70F) converted to 1/kT

    spectrum = (x <= con[0])*pars[0]*np.sqrt(x*kT**3)*np.exp(-x*kT)
    spectrum += (x > con[0])*(x < con[1])*pars[1]/x
    spectrum += (x >= con[1])*pars[2]*np.exp(-x/0.965)*np.sinh(np.sqrt(2.29*x))

    return spectrum

def getCon(pars):
    '''
    After adjusting the normaliztion parameters, need to find the new location
    where we switch from the intermediate spectrum to the fission spectrum.
    This is set to the location where the curves intersect, within a range of
    1 keV and 0.5 MeV.
    '''

    x = np.linspace(1e-3, 5e-1, 5000)

    low = pars[1]/x
    high = pars[2]*np.exp(-x/0.965)*np.sinh(np.sqrt(2.29*x))

    diff = low - high
    # first check the scenarios where we the intersection would
    # be below or above the cutoff regions
    if len(diff[diff > 0.]) == len(diff): # if low is always higher, then choose max value
        return 5e-1
    elif len(diff[diff < 0.]) == len(diff): # if high is always larger, then choose min value
        return 5e-1

    con = x[1:][np.diff(np.sign(diff)).astype(bool)][0]
    
    return con

def getRatios(df, iso):

    if 'high_low' in df.columns:
        df.loc['high_low'] = df.apply(lambda row: iso['spec'][row['isotope']], axis=1)
    else:
        df['high_low'] = df.apply(lambda row: iso['spec'][row['isotope']], axis=1)
    df_high = df[df['high_low'] == 'fission']
    df_low = df[df['high_low'] == 'thermal']

    # do some checks to make sure that we don't try to divide any empty dfs
    if len(df.index):
        ratio = (df['sat act']/df['calc act']).mean()
    else:
        ratio = 1
    if len(df_high.index):
        ratio_high = (df_high['sat act']/df_high['calc act']).mean()
    else:
        ratio_high = 1
    if len(df_low.index):
        ratio_low = (df_low['sat act']/df_low['calc act']).mean()
    else:
        ratio_low = 1

    return ratio, ratio_high, ratio_low

def calc1MeV(spectrum, damage, energy):
    '''
    Calculate the 1 MeV equivilent neutron flux for the for the given
    neutron energy spectrum based on the silicon damage function
    '''

    flux = spectrum[:-1]*damage*(energy[1:] - energy[:-1])
    #print(flux)
    #print(np.sum(flux))
    return np.sum(flux)*10**24 # convert from bn to cm^-2

if __name__ == '__main__':
    #print(getXsec('inputs', []))
    pass
