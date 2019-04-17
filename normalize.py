import ROOT as r
import numpy as np
import argparse
import array
from decimal import Decimal

parser = argparse.ArgumentParser(description = 'State name of output file you are getting your fit parameters from')
parser.add_argument('-a', '--activity', type=str, required=True, help='Name of activity file you are using')
parser.add_argument('-f', '--file', type=str, default='fit_output_8-inch.txt', help='Name of file you are getting fit params from')
#parser.add_argument('-p', '--plot', type=int, default=0, help='Plot spectrum')
parser.add_argument('-p', '--plot', action='store_true', help='Plot spectrum')

con1 = 0.0
con2 = 0.0
temperature = 3.93E7

# Creates an object which contains the following foil properties:
#   isotope, cross section, measured activity, calculated activity,
#   whether it has cd shielding, if it is activated by thermal or fission neutrons
# All of the foils calculations are contained in the class methods
class foil():

    xsec = []
    energy = []
    name = ''
    measAct = 0.0
    calcAct = 0.0
    ratio = 0.0
    low_high = 0
    cd = ''
    cd_xsec = []
    cd_thick = 0.025 #units of inches, need to convert to nuclei/bn
    # this conversion is: inch -> cm -> g/cm^2 -> N/cm^2 -> N/bn
    cd_thick = ( cd_thick*(2.54) )*(8.65) / ( 112.414/6.02E23 ) / (10**24)
    inCd = False

    def __init__(self, foil, act, cd, low_high):
        self.name = foil
        self.measAct = float(act)
        self.cd = cd
        self.low_high = low_high
        if self.cd == 'cd':
            self.inCd = True
            print self.name, self.cd_thick

    def calculateAct(self, spectrum):
        print 'calculating act for:', self.name
        self.calcAct = 0.0
        assert len(self.energy)-1 == len(self.xsec)
        for i in range(len(self.energy)-1):
            if i == 0:
                pass
                #continue
            self.calcAct += spectrum.Eval(self.energy[i])*self.xsec[i]*(self.energy[i+1]-self.energy[i])
        self.ratio = self.measAct/self.calcAct

    def readXSec(self):
        xsec = []
        cd_xsec = []
        f = open('inputs/%s.txt' % self.name, 'r').readlines()
        for line in f:
            xsec += [float(val) for val in line.split()]
        #f.Close()
        if self.inCd:
            cd_f = open('inputs/cd_case.txt', 'r').readlines()
            for line in cd_f:
                cd_xsec += [self.cd_thick*float(val) for val in line.split()]
            xsec = [foil*np.exp(-cd) for foil, cd in zip(xsec, cd_xsec)]
        np.asarray(xsec)
        self.xsec = xsec

    def cdXsec(self):
        xsec = []
        f = open('inputs/cd_case.txt', 'r').readlines()
        for line in f:
            xsec +=[float(val) for val in line.split()]
        np.asarray(xsec)
        self.cd_xsec = xsec

# Reads the activity file and creates a foil object for each foil
# These are then stored in a dictionary
# Information must be formed in the following way:
#   foil, meas_act, in shielding (null or cd), neutron type (thermal or fission)
def readAct(filename):
    f = open(filename).readlines()
    foils = {}
    low_high = 0
    for line in f:
        par = line.split(',\t')
        if 'cd' in par[-2]:
            key = '%s_cd' % par[0]
        else:
            key = par[0]
        if 'fission' in par[-1]:
            low_high = 1
        elif 'thermal' in par[-1]:
            low_high = 0
        else:
            print 'Last param must be thermal or fission'
            quit()
        #foils[line.split(',\t')[0]] = foil(line.split(',\t')[0], float(line.split(',\t')[1]), line.split(',\t')[2])
        foils[key] = foil(par[0], par[1], par[2], low_high)
    return foils

def readXSec(foil):
    f = open('inputs/%s.txt' % foil, 'r').readlines()
    xsec = []
    for line in f:
        xsec += [float(val) for val in line.split()]
    np.asarray(xsec)
    return xsec

def readPar(filename):
    f = open(filename, 'r').readlines()
    pars = np.zeros(3)
    nextline = False
    global con1
    global con2
    for line in f:
        if 'Thermal Scale' in line:
            pars[0] = float(line.split(':\t')[-1])
        if 'Interm Scale' in line:
            pars[1] = float(line.split(':\t')[-1])
        if 'Fission Scale' in line:
            pars[2] = float(line.split(':\t')[-1])
        if nextline:
            con1 = float(line.split(',\t')[0])
            con2 = float(line.split(',\t')[1])
            nextline = False
        if 'Connection' in line:
            nextline = True
    pars.tolist()
    return pars

def getDamage():
    f = open('inputs/si_damage.txt', 'r').readlines()
    damage = []
    energy = []
    for line in f:
        energy.append(float(line.split(',')[0]))
        damage.append(float(line.split(',')[1]))
    return damage, energy

# The function used to model the neutron energy spectrum
def func(x, par):
    spectrum = (x[0] < con1)*par[0]*r.TMath.Sqrt(x[0]*temperature**3)*r.TMath.Exp(-x[0]*temperature)
    spectrum += (x[0] > con1)*(x[0] < con2)*par[1]/x[0]
    spectrum += (x[0] > con2)*par[2]*r.TMath.Exp(-x[0]/0.965)*r.TMath.SinH(r.TMath.Sqrt(2.29*x[0]))
    return spectrum

# Next two functions are used to recalculate the connection regions between the thermal and intermediate spectrum
def get_con_helper(x, par):
    func1 = par[0]*r.TMath.Sqrt(x[0]*temperature**3)*r.TMath.Exp(-x[0]*temperature)
    func2 = par[1]/x[0]
    func = func1 - func2
    return func

def get_con(par):
    global con2
    func = r.TF1('high func', get_con_helper, 1E-3, 1, 2)
    func.SetParameters(par[1], par[2])
    wf = r.Math.WrappedTF1(func)
    root = r.Math.BrentRootFinder()
    root.SetFunction(wf, 1E-3, 5E-1)
    root.Solve()
    con2 = root.Root()

# Calculates the 1 MeV equivilent flux using the 
def calc1MeV(spectrum, damage, damage_energy, useThermal):
    equiv = 0.0
    if useThermal:
        pass
    else:
        spectrum.SetParameters(0,spectrum.GetParameter(1),spectrum.GetParameter(2))
    for i in range(len(damage_energy)-1):
        #print damage_energy[i], spectrum.Eval(damage_energy[i])
        equiv += spectrum.Eval(damage_energy[i])*damage[i]*(damage_energy[i+1]-damage_energy[i])
    return equiv

# Makes a plot of the normalized function
def MakePlot(func, pars, outname):
    c = r.TCanvas('c', 'c', 800, 600)
    func.SetParameter(0,pars[0]*10**24)
    func.SetParameter(1,pars[1]*10**24)
    func.SetParameter(2,pars[2]*10**24)
    func.GetYaxis().SetTitle('Neutron Flux (n/MeV/cm^2/s')
    func.GetXaxis().SetTitle('Energy (MeV)')
    func.GetYaxis().SetTitleOffset(1.15)
    func.GetXaxis().SetTitleOffset(1.1)
    c.SetLogx()
    c.SetLogy()
    c.SetGrid()
    func.Draw()
    c.SaveAs('normalized_spectrum.png')
    c.SaveAs('plots/%s.png' % outname.split('.')[0])

def main():
    args = parser.parse_args()

    print 'Reading Input Files'
    foils = readAct(args.activity)
    print foils.keys()
    energy = readXSec('energy')
    #energy.append(20)
    damage, damage_energy = getDamage()
    damage_energy.append(20)
    
    fit_file = 'fit_outputs/%s' % args.file
    pars = readPar(fit_file)

    fout = open('normalization_outputs/%s' % args.activity, 'w')

    print 'Spectrum parameters are:', pars, con1, con2
    spectrum = r.TF1('spectrum', func, 1E-10, 20, len(pars))
    spectrum.SetParameters(array.array('d', pars))
    #for i in range(len(pars)):
    #    spectrum.SetParameter(i, array.array('d', pars[i]]))
    print '1 MeV Equiv Flux of initial flux is:', calc1MeV(spectrum, damage, damage_energy, True)*10**24

    print 'Getting foil cross sections and calculating activities'
    print 'Ratio of meas_act/calc_act for each foils is:'
    fout.write('Original ratio of meas_act/calc_act for each foils is:\n')
    fout.write('foil,\tmeas act,\tcalc act,\t meas/calc\n')
    for foil in foils:
        #foils[foil.name].xsec = readXSec(foil)
        foils[foil].readXSec()
        #if foils[foil].inCd:
        #    foils[foil].cdXsec()
        foils[foil].energy = energy
        foils[foil].calculateAct(spectrum)
        print foil, foils[foil].measAct, foils[foil].calcAct, foils[foil].ratio
        fout.write('%s,\t%.2E,\t%.2E,\t%.4f\n' % (foil, Decimal(foils[foil].measAct), Decimal(foils[foil].calcAct), foils[foil].ratio))

    # Getting ratio values
    avg_ratio = sum([foils[foil].ratio for foil in foils])
    low_ratio = sum([foils[foil].ratio for foil in foils if foils[foil].low_high == 0])
    high_ratio = sum([foils[foil].ratio for foil in foils if foils[foil].low_high == 1])

    avg_ratio = avg_ratio/len(foils)
    if not len([foils[foil] for foil in foils if foils[foil].low_high == 0]) == 0:
        low_ratio = low_ratio/len([foils[foil] for foil in foils if foils[foil].low_high == 0])
    else:
        low_ratio = 0
    high_ratio = high_ratio/len([foils[foil] for foil in foils if foils[foil].low_high == 1])

    print 'Average meas_act/calc_act value before normalization is:', avg_ratio
    print 'Average thermal ratio:', low_ratio
    print 'Average fission ratio:', high_ratio

    fout.write('\nAverage meas_act/calc_act before normalization is:  %.4f\n' % avg_ratio)
    fout.write('Average thermal ratio:  %.4f\n' % low_ratio)
    fout.write('Average fission ratio:  %.4f\n' % high_ratio)

    #pars = pars*avg_ratio
    pars = pars*low_ratio
    pars[2] = pars[2]*high_ratio/low_ratio
    get_con(pars)
    spectrum.SetParameters(array.array('d', pars))
    #for i in range(len(pars)):
    #    spectrum.SetParameter(i, array.array('d', [pars[i]]))
    print '\nAdjusted normalization so new ratio is 1.0\nnew ratio for foils are:'
    fout.write('\nAdjusted normalization so new ratio is 1.0.\nThe activity values and ratio for foils are now:\n')
    fout.write('foil,\tmeas act,\tcalc act,\t meas/calc\n')
    for foil in foils:
        foils[foil].calculateAct(spectrum)
        print foil, foils[foil].calcAct, foils[foil].ratio
        fout.write('%s,\t%.2E,\t%.2E,\t%.4f\n' % (foil, Decimal(foils[foil].measAct), Decimal(foils[foil].calcAct), foils[foil].ratio))

    avg_ratio = sum([foils[foil].ratio for foil in foils])/len(foils)
    print 'Average ratio after normalization is:', avg_ratio
    fout.write('\nAverage ratio after normalization is:  %.4f\n' % avg_ratio)

    print '1 MeV equivalence is now:'
    Thermal1MeV = calc1MeV(spectrum, damage, damage_energy, True)*10**24
    noThermal1MeV = calc1MeV(spectrum, damage, damage_energy, False)*10**24
    print 'With thermal spectrum:', Thermal1MeV
    #print 'Without thermal spectrum:', noThermal1MeV
    print 'New Paramters are:', pars
    print 'New Connection Regions Are:', con1, con2

    fout.write('\nNormalized 1 MeV equivalence is:  %.2E n/cm^2/s\n\n' % Decimal(Thermal1MeV))

    fout.write('New function parameters are:\n')
    fout.write('Thermal:\t%.2E\n' % Decimal(pars[0]))
    fout.write('Intermediate:\t%.2E\n' % Decimal(pars[1]))
    fout.write('Fission:\t%.2E\n' % Decimal(pars[2]))
    fout.write('Thermal-Interm Connection:\t%.2E\n' % Decimal(con1))
    fout.write('Interm-Fission Connection:\t%.2E\n' % Decimal(con2))

    fout.close()

    if args.plot:
        MakePlot(spectrum, pars, args.activity)

if __name__ == '__main__':
    main()
