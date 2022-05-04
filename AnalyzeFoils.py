import os, sys
import pandas as pd
import numpy as np
import json
import argparse

from ReadFile import *
from SaturatedActivityCalc import *
from NormalizeSpectrum import *

parser = argparse.ArgumentParser(description = 'Takes foil irradiation measurements and obtains a fluence for the irradiation.')
parser.add_argument('-f', '--file', type=str, help='Input file in .xls, .odf, or csv plaintext format which contains the filled out foil info')
parser.add_argument('-o', '--overwrite', action='store_true', help='Save the updated table over the original input file. Note that doing this will not modify any of the user entered values. If this option is not specified, new output file will be produced.')
parser.add_argument('--makeTemplate', type=int, help='Will produce a .xls file that can be filled in and later read by script.')
parser.add_argument('--isotopePath', type=str, default='inputs', help='Folder which contains various physical information about activated isotopes. In github this is "inputs".')
parser.add_argument('--isotopeConstants', type=str, default='IsotopeInfo.json', help='JSON file which contains halflife of daughter isotope, fraction of naturally occuring element of mother isotope, nuclear mass of mother isotope, and whether the isotope is primarily activated by thermal or fission neutrons. Expected to be in the isotopePath directory.')
parser.add_argument('--damageFunction', type=str, default='si_damage.txt', help='File which holds the silicon damage function and its energy binning. Expected to be in the isotopePath directory.')
parser.add_argument('--spectrumDir', type=str, default='fit_outputs', help='Directory which contains the initial neutron spectrums which are normalized during fluence calculating procedure.')
parser.add_argument('--neutronSpectrum', type=str, default='fit_output_8-inch.txt', help='Set of initial neutron spectrum parameters used for flux normalization and fluence calculation. Expected to be in the spectrumDir directory.')
args = parser.parse_args()


def main():
    
    # First check if user is just trying to produce a template
    if args.makeTemplate is not None:
        if not args.makeTemplate > 0:
            print('Error: need to pass an int greater than 0 after --makeTemplate')
        else:
            makeTemplate( args.makeTemplate )
        quit()

    # Next need to make sure that an input file is being specified
    if args.file is None:
        print('Error: If not producing a template, need to specify an input .xls or csv file with foil data')
        print('Basic script usage:  python AnalyzeFoils.py -f foilmeasurements.xls')
        quit()


    # Obtain the foil information and calcualte the activity at the end of the irradiation and activity at saturation
    fdata = makeDF(args.file)
    iso_info = json.load(open('%s/%s' % (args.isotopePath, args.isotopeConstants), 'r'))

    fdata['init act'] = fdata.apply(lambda row: calcInitAct(row['meas act'], row['wt'], iso_info['hl'][row['isotope']]), axis=1) 
    fdata['sat act'] = fdata.apply(lambda row: calcSatAct(row['init act'], row['it'], iso_info['hl'][row['isotope']], iso_info['nm'][row['isotope']], row['mass'], iso_info['frac'][row['isotope']]), axis=1)
    print('\n')
    print(fdata)

    # Extract cross section information about the measured isotopes
    # and construct the initial neutron spectrum which will be re-normalized
    xsec = getXsec(args.isotopePath, fdata['isotope'].unique().tolist())
    pars, cons = readSpectrum('%s/%s' % (args.spectrumDir, args.neutronSpectrum) )
    damage = getDamage('%s/%s' % (args.isotopePath, args.damageFunction))
    spectrum = makeSpectrum(xsec['energy'], pars, cons)

    # Obtain an initial set of calculated activities based on the initial spectrum
    # Additionally, produce the flux and fluence columns now, so we don't have to do with when normalizing
    # spectrum based on a foil by foil basis
    fdata['calc act'] = fdata.apply(lambda row: calcAct(spectrum, xsec[row['isotope']], xsec['energy']), axis=1)
    fdata['flux'] = calc1MeV(makeSpectrum(damage['energy'], pars, cons), damage['damage'], damage['energy'])
    fdata['fluence'] = fdata.apply(lambda row: row['flux']*row['it']*60*60, axis=1) # convert it (in hours) to seconds

    print('\n')
    print(fdata)

    # Check if a single fluence should be calculated for all foils together (y) 
    # or if a separate fluence should be calculated for each foil (n)
    if len(fdata['Foil'].unique()) > 1:
        print('\n')
        print('>> Found more than one foil listed in the input file %s' % args.file)
        choice = input('>> Do you want to calculate a single fluence based on all foils (y) or a separate fluence for every foil (n)?\n')
        while True:
            if choice.lower() == 'y':
                print('>>>> Will calculate a single fluence based on all foil activities')
                do_all = True
                break
            elif choice.lower() == 'n':
                print('>>>> Will calculate a separate fluence for each foil')
                do_all = False
                break
            else:
                choice = input('>>>> Did not understand your input "%s", please enter y or n\n' % choice)
    else:
        print('>> Found one foil listed in the input file %s' % args.file)
        do_all = True

    sub_dfs = []
    if not do_all:
        for foil in fdata['Foil'].unique().tolist():
            sub_dfs.append(fdata[fdata['Foil'] == foil].copy())
    else:
        sub_dfs.append(fdata)
        
    pars_i = pars.copy() # need to make sure we do normalization w.r.t. the initial spectrum parameters
    for df in sub_dfs:

        print('\n')
        if do_all:
            print(">> Running normalization over all foils")
        else:
            print(">> Running spectrum normalization over %s" % df['Foil'].iloc[0])
        # obtain the correction ratios for the thermal+intermediate and fission neutron spectrums
        ratio, high, low = getRatios(df, iso_info)

        print(">>>> Average ratio before normalziation is ", ratio, high, low)

        # use the ratios to adjust the initial normalizations
        pars[0] = low*pars_i[0]
        pars[1] = low*pars_i[1]
        pars[2] = high*pars_i[2]
        # find the new energy value where the spectrum changes from intermediate to fission
        cons[1] = getCon(pars)

        print(">>>> Spectrum normalization and connection paramters computed as:", pars, cons)

        # Recalculate the activity, flux, and fluence with the updated spectrum normalizations
        spectrum = makeSpectrum(xsec['energy'], pars, cons)
        df.loc[df.index, 'calc act'] = df.apply(lambda row: calcAct(spectrum, xsec[row['isotope']], xsec['energy']), axis=1)
        df.loc[df.index, 'flux'] = calc1MeV(makeSpectrum(damage['energy'], pars, cons), damage['damage'], damage['energy'])
        df.loc[df.index, 'fluence'] = df.apply(lambda row: row['flux']*row['it']*60*60, axis=1) # convert it (in hours) to seconds

        print(">>>> Measured flux is: %.4f" % df['flux'].iloc[0])
        print(">>>> Measured fluence is %.4f:" % df['fluence'].iloc[0])

        if do_all:
            fdata = df
        else:
            idxs = fdata.index[fdata['Foil'] == df['Foil'].iloc[0]].tolist()
            fdata.loc[idxs, ['calc act', 'flux', 'fluence']] = df[['calc act', 'flux', 'fluence']]

    print('\nNew dataframe is:')
    print(fdata)

    if args.overwrite:
        print('Saved dataframe as: %s' % args.file)
        if '.xlf' in args.file or args.file.endswith('.odf'):
            fdata.to_excel(args.file)
        else:
            fdata.to_csv(args.file, index=False)
    else:
        # Use a minimal-assumption way to append _analyzed to the portion of the file name before the 
        # final extension because who knows, maybe someone in 3 years will have extra . in the filename
        f_ext_len = len(args.file.split('.')[-1])+1 # +1 because need to include the .
        f_pre = args.file[:-1*f_ext_len]
        f_ext = args.file[len(f_pre):]
        f_new = f_pre+'_analyzed'+f_ext
        print('Saved dataframe as: %s' % f_new)
        if '.xlf' in f_new or f_new.endswith('.odf'):
            fdata.to_excel(f_new)
        else:
            fdata.to_csv(f_new, index=False)
        


if __name__ == '__main__':
    main()
