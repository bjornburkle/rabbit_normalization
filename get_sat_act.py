import math
from decimal import Decimal

#####################################################################
# Put the input in the following order:                             #
# isotope, activity, wait time,                                     #
# values must be tab delimated. If isotopes were already back       #
# calculated, put a wait time of 0.                                 #
#####################################################################

import argparse
parser = argparse.ArgumentParser(description = 'Give the name of the input file and the irradiation time.')
parser.add_argument('-f', '--file', type=str, required=True, help='Name of the input file which will contain the measurements. It is assumed that this file is in the "measurements" directory')
parser.add_argument('-i', '--irrad_time', type=float, required=True, help='The length of the irradiation time, in hours')
args = parser.parse_args()

hl = {
  'Al': 14.959,
  'Fe54': 7489.44,
  'Fe56': 2.5789,
  'Fe58': 1067.88,
  'Zr': 78.41,
  'Cu': 12.7,
  'Co': 46165.2
}

for key in hl:
    hl[key] = math.log(2)/hl[key]

frac = {
  'Al': 1,
  'Fe54': 0.0585,
  'Fe56': 0.9175,
  'Fe58': 0.0028,
  'Zr': 0.5145,
  'Cu': 0.6915,
  'Co': 0.00116*(0.6/1000) # This is the % of mass in CoAl wire multiplied by it's mass per unit length in g/m
}

nm = {
  'Al': 27,
  'Fe54': 54,
  'Fe56': 56,
  'Fe58': 58,
  'Zr': 90,
  'Cu': 63,
  'Co': 59
}

class foil():
    
    def __init__(self, foil, act, mass, wait_time, rad_time):
        self.foil = foil
        self.decay = hl[foil]
        self.frac = frac[foil]
        self.nm = nm[foil]
        self.act = float(act)
        self.rad_time = float(rad_time)
        self.mass = float(mass)
        self.wait_time = float(wait_time)

    def init_act(self):
        self.act = self.act*math.exp(self.wait_time * self.decay)
        print 'Initial activity for %s was %.2E uCi' % (self.foil, Decimal(self.act))

    def sat_act(self):
        self.act = self.act / (1 - math.exp(-self.rad_time * self.decay) )
        self.act = 3.7e4 * self.act * self.nm / (self.mass * 6.02e23 * self.frac)
        print 'Saturated activity for %s is %.2E decays/nuclei/s' % (self.foil, Decimal(self.act))

def ReadFile(filename):
    filename = 'measurements/%s' % filename
    foils=[]
    f = open(filename, 'r').read().splitlines()
    print 'Calculating Activites For:'
    for line in f:
        if len(line) == 0:
            continue
        meas = line.split(',\t')
        meas.append(args.irrad_time)
        print meas[0]
        foils.append(foil(*meas))
    return foils

def main():
    foils = ReadFile(args.file)
    print 'Calculating initial activities'
    for foil in foils:
        foil.init_act()
    print 'Calculating saturated activities'
    for foil in foils:
        foil.sat_act()

    print 'Writing activity file'
    fout = open('activities/act_%s'%args.file, 'w')
    for i, foil in enumerate(foils):
        fout.write('%s,\t%.3E,\t' % (foil.foil, Decimal(foil.act)))
        fout.write('<cd or null>,\t<thermal or fission>')
        if i+1 != len(foils):
            fout.write('\n')
    print 'Script has finished'
    print 'Before running normalization.py, specify in the output file whether each foil was in cd or not, and whether it is primarily effected by thermal or fission neutrons.'

if __name__ == '__main__':
    main()
