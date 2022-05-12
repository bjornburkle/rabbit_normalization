# ReadMe

The code contained in this repo is used to analyze the measured activity of foils iron irradiated inside of the RINSC neutron reactor and calculate an experienced fluence for each foil. The code can also be used to analyze the activity using Al, Cr, and Zr foils as well as Co in the form of CoAl wires. However, at the current time there are only plans to include Fe foils due to the presence of three separate naturally occuring isotopes (Fe54, Fe56, and Fe58) which undergo neutron activation.

# Running the Code 

The code is designed to be run using python3 and requires the following python3 libraries must be installed:<br/>
 - os
 - sys
 - io
 - math
 - numpy
 - pandas
 - argparse

## Producing an Input File

To produce a file of the proper format, the following command can be run:

`python AnalyzeFoils.py --makeTemplate n`

where `n` is an int signifying the number of foil entries that will be created in the template. The output file `inputTemplate.xls` will be created, which can be opened using excel or an equivalent application. The foils will be uniquely identified through their name in the **Foil** column. For each foil three separate rows are automatically created, one for each of the three neutron activated isotopes. The name used in the **Foil** column can be edited as long as each foil has a unique name in the column, and all isotopes beloning to the same foil share the same foil name.

After generating the script, the user will need to fill in the information in the **mass**, **irradiation time (h)**, **wait time (h)**, and **meas act** columns.<br/>
 - **mass**: The mass of the foil in grams.
 - **irradiation time**: The time (in hours) that the foil(s) were irradiated for. For rabbit irradiations, this is normally the time between the tube being sent to to the reactor core and being sent back. For beamport irradiations, this is normally the amount of time that the reactor is at full power.
 - **wait time (h)**: The time (in hours) between the time the time that the irradiation ended and the time that the gamma spectroscopy used to measure the activity of the daughter isotopes began. For best accuracy, the difference in time rounded to the nearest minute should be computed.
 - **meas act**: The measured activity of the daughter isotope as obtained from the gamma spectroscopy report. The activation will be in units of uCi and information about obtaining these values from the gamma spectroscopy output files is decribed further below in the readme. If an isotope was not measured, this value can be left blank and the code will know to omit it when reading the input file.

#### Additional Notes:

 - For foils will multiple rows, the **mass**, **irradiation time**, and **wait time** only needs to be filled for a single row.
 - Isotopes beyond the three iron foils can be used and should be entered as the \<Iso\> in the **isotope** column. However, the cross section in the irdf-640 energy bins must be included as `inputs/\<Iso\>.txt` placed in the directory and the halflife, fraction of the naturally occuring element that is the mother isotope, the nuclear mass of the isotope, and whether the activation cross section is dominated by the fission or thermal neutron spectrum should be included in `inputs/IsotopesInfo.json`.
 - If running on a computer which has no excel or equivilent program, the code can also be run on csv files. For csv files, the first row of the file must be a header which includes the same columns names as the .xls files created from the `--makeTemplate` argument.


## Analyzing the Foil Measurements

To analyze the foils and extract the fluence, the followiung command must be run:

`python AnalyzeFoils.py -f /path/to/foilData.xls`

The `-o` argument can also be to turn on the `--overwrite` parameter to write over the input file after adding additional columns for the saturated activity, flux, and fluence calculated for each of the foils. The `-h` parameter can also be used to see additional arguments which can be passed to modify the directories and files used to hold various other script inputs.

------------------------------------------------------------------------

If running the script over an input with more than one foil, you will be asked<br/>
`>> Do you want to calculate a single fluence based on all foils (y) or a separate fluence for every foil (n)?`<br/>
Responding with `n` will calculate a unique flux and fluence value for each foil, and is the standard procedure when analyzing foils. Responding with `y` will calculate a common flux based off of the activity measurements of all the foils in the input file.

After the script has finished, the name of the output file will be printed along the bottom of the terminal. In the case that the `-o` argument was not used, the output file will take the name of the original file and append `_analyzed` before the extension. This will contain the original input table with the measured saturated activity, the saturated activity from the derived neutron flux, the 1 MeV equivilent neutron flux, and 1 MeV equivelant nuetron fluence values calculated for each foil/isotope.


## Reading the Gamma Spectrum Analysis Files

The measured activity is obtained from the gamma spectrum analysis files which we recieve from the reactor staff. Two spetrcum analysis files are included in this repo as an example. Unfortunately, information about the foils and irradiation in which they took part in is inconsistent. However, the name of the pdf and the **Sample Title** and **Sample Desciption** fields on the first page of the report often include information about the mass of the foil, the length of the irradiation, and the time that the sample left the reactor/when the beamport irradiation ended. If any of this information is missing from the file, you will need to check with the reactor staff and/or the current lab researcher in regular communication with the reactor staff about any missing details.

When calculating the **wait time (h)** for the foil analysis, it is important to use the time between the end of the irradiation and the date/time listed in the **Acquisition Started** field on the first page of the report.

To obtain the activities used to fill the **meas act** field of the foil analysis input files, the activity values obtained from the **Interference Corrected Report** page (normally the second to last page) in the pdf are used. The activity is obtained by reading the **Wt mean activity** value for the daughter isotope of the activation process that is being measured to determine the neutron flux. For Iron, we are interested in the Fe54(n,p)Mn54, Fe56(n,p)Mn56, and Fe58(n,gamma)Fe59 activation processes. In other words, the **Wt mean activity** value for the Mn54 isotope decay is what would be entered for the Fe54 field when filling out the `inputTemplate.xls`.

### Notes

 - Because Mn56 only has a half-life of approximately 2.5 hours, it is common for all of the Mn56 to decay for wait times longer than ~30 hours. As such, there will be no Mn56 entry in the **Interference Corrected Report** page of the spectrum analysis file and the corresponding Fe56 entry in the foil analysis input file will need to be left unfilled.
 - Occasionally the reactor staff will accidentally produce reports which back calculated the activity. When this happens, the **Wt mean activity** values reported on the **Interference Corrected Report** page of the spectrum analysis files will be adjusted to the activities they would have had at the end of the analysis. This is easy to notice when calculating the flux, because only the Mn56 has a short enough half-life to be effected by the back calculation. This will lead to the Mn54 and saturated activity being consistent with expectations based on previous irradiations, but an Mn56 saturated acitivty that is orders of magnitude too high. When this happens, it can be remedied by setting the **wait time (h)** value for the corresponding foil to 0.

## Additional Information about the Files

The code is written to be highly modular and minimize the amount of hard coded values. To further compartmentalize the code, the functions being used to perform the analysis are split into three distinct files. A brief descriptions of the files is given below. More in depth descriptions of each of the functions including their purpose and a description of their inputs can be found inside each of the scripts.
 - `ReadFile.py` contains the function to produce the input file template and the function to read the filled input file.
 - `SaturatedActivityCalc.py` contains the functions used to internally perform a back calculation and to calculate the saturated activity.
 - `NormalizeSpectrum.py` contains the various functions required to calculate the flux based on the measured actities of the various foil isotopes which have been converted to saturated activities. Inside of the script the functions can be split into the following types: Functions used to read the various information from the `inputs` directory, functions used to build the neutron energy spectrum, the functions used to normalize the assumed neutron energy spectrum, and the functions used to calculate the 1 MeV equivilent flux.
 - AnalyzeFoils.py is the primary script which calls the functions contained in the other files. The script also contains the parser which can be used to set various input pathways for reading auxilary input files.
