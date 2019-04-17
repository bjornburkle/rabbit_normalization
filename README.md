# READ ME

## These files are used to analyze the foil measurements and get a flux for the rabbit system. This documentation will go through what all needs to be done to go from a gamma spectrum analysis given to us by the reactor staff, obtain the saturated activity measurements, and from those obtain a normalized rabbit system flux.

## Gamma Spectrum Analysis

Two of the gamma spectrum analysis documents are obtained in this git repository. This can be used as an example for how to obtain the necessary information. On the first page of the reportm you should see the name of the sample, when the acquisition was started, and when the irradiation started. Note that some reports specify when the sample was put into the reactor, and others mention when the irradiation ended.

Given the time values, you need to record how much time passed between the END of the irradiation, and the START of the acquisition time.

The other values which must be recorded are the measured activity value. For the sample document, these values can be found on page 7 of "Fe foil 3e14.PDF" and page 8 of "Fe F foil 6e14.PDF" (Interference Corrected Report). From here, you can obtain the activity (under Wt mean Activity) for the daughter isotope of the decay. Because we are only interested in the activation of the Iron and Cobalt, we are only interested in the following activations:

Fe54->Mn54
Fe56->Mn56
Fe58->Fe59
Co59->Co60

Once all of these values are recorded, you can go on to calculating the saturated activity of these foils.

### Note

Do note that in the example documents, the measurements for "Fe F foil 6e14.PDF" were back calculated. This can be inferred from the measured activity of the Fe56->Mn56 decay. Foils are normally measured about 24 hours after the irradiation takes place, and we expect the Mn56 activty to be on the order of 10^-3 or 10^-4 uCi. For back calculated values, they would normally be on the order of 10^-1 uCi.

## Saturated Activity Calculation

To obtain the saturated activity values, you must run the python script get_sat_act.py
For an example, I have included the file meas_test.txt. This includes the foil irradiations for the 6e14 irradiation on 2/13/2019. These foils were irradiated for 27 minutes. (Note: we obtained this value back calculated. However, I obtained the initial activity by undoing the back calculation.)

The python script will calculate both the initial activities (the acitivity of the various isotopes at the end of the irradiation) and the corresponding saturated activity values. The initial activity values will be printed to the terminal, but not recorded. However, the saturated activity values will be saved to an output file.

The script uses a parser which requires two inputs, the name of the file which obtains the activity measurements, and the irradiation time. You can type "python get_sat_act.py -h" to get the following output:

------------------------------------------------------------------------

usage: `get_sat_act.py [-h] -f FILE -i IRRAD_TIME`

Give the name of the input file and the irradiation time.

optional arguments:
  `-h`, `--help`            show this help message and exit
  `-f FILE`, `--file FILE`  Name of the input file which will contain the
                        measurements
  `-i IRRAD_TIME`, `--irrad_time IRRAD_TIME`
                        The length of the irradiation time, in hours

You would run the example script in the following way:

------------------------------------------------------------------------

 `python get_sat_act.py -f meas_test.txt -i 0.45`

For get_sat_act.py measurements must be entered with the following format:
foil,	meas\_act,	foil\_mass,	wait\_time

Note that these script to run, these values must be delimated using a comma followed by a tab.

The variables represent the following values:

--foil:
The name of the foil which is being activated. Note that in the case of iron, you must also specify the isotope since there are multiple isotopes which are being activated for this foil. In this script, the name of the foil is used to obtain some physics properties of the isotope and it's daughter isotopes which are stored in the script as python dictionaries

--meas\_act:
The activity measurement, measured in uCi, which was recorded from the gamma spectroscopy analysis

--foil\_mass:
In the case of iron, this is the mass of the foil (in grams) which was irradiated. For the case of the CoAl wire, this is the length (in mm) of the wire. The script will then use the wire density and percent of Co in the wire to compute the mass of the Co (in grams).

--wait\_time:
The time recorded from the gamma spectroscopy analysis. Note that if the activity values were calculated, two things can be done. If you input a value of 0, it will simply calculate the saturated activity of those values. If you input the value as the negavite of the weight\_time (for the iron, this would be -26.65), the "Initial Activity" values output in the terminal window will actually be the true measured activity values (if there was no back calculation). However, note that if you put in a negative weight time, the saturated activity value will definitely be incorrect.

After running the script, you will obtain an output file. The output file will be the same name as the input file, but with "act\_" appended to the start of the file name. This file is already in a format which can be fed into the `normalization.py` script. However, some edits will need to be made to the output file before it can be run through the script.

### Note, in order to make sure that the values you obtained make sense, these are the average values obtained from all past rabbit system irradiations:

Fe54:  2.21E-14
Fe56:  2.78E-16
Fe58:  5.04E-12
Co:    7.46E-11

## Rabbit Flux Normalization

This script will take the saturated activity measurements obtained using `get_sat_act.py` and use those values to find a rabbit system normalization of the 8-inch beam port energy spectrum. It does this by applying two different normalizations. Foils which are senstive to thermal neutrons will put a normalization on the Thermal and Intermediate spectrum. Foils which are sensetive only to fission neutrons will apply a normalization to the intermediate spectrum.

From the previous script, you will obtain the output file act\_meas\_test.txt. This file is already in the format needed to feed into `normalization.py`but requires some editing. Once again, the formatting of the information are:
foil,	sat\_act,	covered,	neutrons\_sensetivity

Where the values are delimated using a comma followed by a tab. The values listed represent the following things:

--foil:
Same as for the `get_sat_act.py` script. This value is automatically entered when this file is created

--sat\_act:
This is the saturated activity as calculated in the `get_sat_act.py` script. Once again, these measurements are automatically entered into the input file

--covered:
This states whether or not the foil was encased in cadmium. If it was covered, put `cd` in this space. If not, put `null`. (Note, you can technically put anything in place of `null` and the script will act the same way)

--neutrons\_sensetivity
Whether the foil primarily sensetive to thermal or fission neutrons. For `Co` and `Fe58`, you would put `thermal` in this field. For `Fe54` and `Fe56` you would enter `fission` into this field.


Once the proper edits have been made to the input file, `normalize.py` can be read. Once again, the python script uses a parser. Typing `python normalize.py -h` in the terminal outputs the following help statement:

------------------------------------------------------------------------

usage: normalize.py [-h] -a ACTIVITY [-f FILE] [-p]

State name of output file you are getting your fit parameters from

optional arguments:
  `-h, --help`            show this help message and exit
  `-a ACTIVITY, --activity ACTIVITY`
                        Name of activity file you are using
  `-f FILE, --file FILE`  Name of file you are getting fit params from
  `-p, --plot`            Plot spectrum

------------------------------------------------------------------------

Using the `-a` option is required, and will be the name of the saturated activity file that was just entered.
The `-f` option is not reqiuired, but is used if you want to select which spectrum you wish to apply the normalization to. By default, it will normalize the spectrum to the 8-inch beam port. However, you can see the other files that you can select in the `fit_outputs/` folder. For example, if you wish to use the new 6-inch beam port spectrum, you would include `-f fit_output_new-6-inch.txt` in the command line when running the script.
Finally, the `-p` option should be included if you wish to also create a plot of the normalized spectrum. Doing this will save a plot in the current directory (has a default name which will be over written every time the script is run) as well as a plot in the `plot/` directory. The image saved to the `plot/` directory will include the name of the activity input file in its name.



A sample version of a completed input file is seen in `act_test.txt`. As an example, type the following command into the terminal:

 `python normalize.py -a act_test.txt -p`

The script will then run over the saturated activity measurements specialized in the file, and save plots of the spectrum. Information related to the normalization will be printed to the terminal screen, as well being saved to the `rabbit_normalization/` folder.

### In the output files, you will get the following information:

A table containing the saturated activity which was measured (meas act), the saturated activity which was calculated using the original spectrum (calc act), and the ratio of the measured activity/calculated activity.

The average value of the average ratio of meas act/calc act for all of the foils before any normalization has been performed. This also includes the average ratios for just the foils sensetive to thermal neutrons, and the average ratio for just the foils sensetive to fission neutrons.

After printing out these values, the normalizations are then performed.
The file then contains a copy of the first table, but with the saturated activity values which were calculated using the normalized spectrum.

The average ratio of the measured activity/calculated activity is then written again. Because the normalization is performed separately for the thermal and fission regions of the spectrum, this value might be slightly different than 1. However, it should be very close.

Finally, the new set of paraters which are used to define the normalized spectrum are included. This includes the following values:
The amplitude of the termal neutron region, the amplitude of the intermediate neutron region, and the amplitude of the fission neutron region.
I also included the "connection points". These are the energies where we switch from one functional form of the spectrum to another.
