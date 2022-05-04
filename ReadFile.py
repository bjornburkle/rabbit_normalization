import os, sys
import io
import pandas as pd

def makeTemplate(numFoils = 1):
    '''
    Produces a basic spreadsheet that users can fill in with gamma spec data
    Automatically assumes data exists for Fe54, Fe56, and Fe58. However, user can
    add more rows for additional isotopes during data entry.

    Function takes the following input:
        numFoils - Number of different foils table entries should be made for
    '''
    keys = ['Foil', 'mass', 'irradiation time (h)', 'wait time (h)', 'isotope', 'meas act']
    isotopes = ['Fe54', 'Fe56', 'Fe58']

    # produce a csv file that is basically just an empty table
    outCSV = ','.join(keys)+'\n'
    for i in range(numFoils):
        for isotope in isotopes:
            outCSV += 'Foil %d,,,,%s,\n' % (i, isotope)

    data = pd.read_csv(io.StringIO(outCSV))
    data.to_excel('inputTemplate.xlsx', index=False)


def makeDF(inFile):
    '''
    Reads template file as a spreadsheet based on formate from makeTemplate.
    If the file isn't an xls format, will also try to read as a csv file.

    After reading file, will do some basic processing to ensure that the mass,
    irradiation time, and wait time are consistent across a single type of foil.
    '''

    if '.xls' in inFile or inFile.endswith('.odf'):
        fdata = pd.read_excel(inFile)
    else:
        fdata = pd.read_csv(inFile)

    # do some column name simplifying so it's easier to code later
    fdata.rename(columns={"irradiation time (h)": "it", "wait time (h)": "wt"}, inplace=True)
    # removing columns for unmeasured isotopes, normally will be from all the Mn56 decaying
    fdata.dropna(subset=['meas act'], inplace=True)
    print(fdata)

    # Make it so user only needs to enter a single mass, irradiation time, and weight time entry for each foil
    foils = set(fdata['Foil'].tolist())
    for foil in foils:
        subdf = fdata.loc[fdata['Foil'] == foil]
        mass = subdf['mass'].dropna().unique()
        it = subdf['it'].dropna().unique()
        wt = subdf['wt'].dropna().unique()
        assert len(mass) == len(it) == len(wt) == 1, "%s has multiple conflicting entries in mass, irradiation time, or wait time fields" % foil

        fdata.loc[fdata['Foil'] == foil, 'mass'] = mass[0]
        fdata.loc[fdata['Foil'] == foil, 'it'] = it[0]
        fdata.loc[fdata['Foil'] == foil, 'wt'] = wt[0]

    print(fdata)
    return fdata

if __name__ == '__main__':
    #makeTemplate(3)
    makeDF('inputTest.xlsx')
