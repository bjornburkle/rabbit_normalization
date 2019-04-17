# READ ME

## These files are used to analyze foil activations measurements and obtain a flux for the rabbit system. This documentation will go through what needs to be done to go from a gamma spectrum analysis given to us by the reactor staff, to obtaining the saturated activity measurements and a normalized rabbit system flux.

## Gamma Spectrum Analysis

Two of the gamma spectrum analysis documents are obtained in this git repository. This can be used as an example for how to obtain the necessary information. On the first page of a report you should see the name of the sample, when the acquisition was started, and when the irradiation started. Note that some reports specify when the sample was put into the reactor, and others mention when the irradiation ended.

Given the time values, you need to record how much time passed between the END of the irradiation, and the START of the acquisition time. So make sure you double check whether the reactor staff listed the start or end time of the irradiation.

The other values which must be recorded are the measured activity value. For the sample documents, these values can be found on page 7 of "Fe foil 3e14.PDF" and page 8 of "Fe F foil 6e14.PDF" (Interference Corrected Report). Note that you will find activity measurements on the previous page(s) as well. However, those are the raw measurements which have not yet been corrected.
From here, you can obtain the activity (under Wt mean Activity) for the daughter isotope of the decay. Because we are only interested in the activation of the Iron and Cobalt, we are only interested in the following activations:

Fe54->Mn54<br/>
Fe56->Mn56<br/>
Fe58->Fe59<br/>
Co59->Co60<br/>

Once all of these values are recorded, you can go on to calculating the saturated activity of these foils.

### Note

Do note that in the example documents, the measurements for "Fe F foil 6e14.PDF" were back calculated. This can be inferred from the measured activity of the Fe56->Mn56 decay.
Foils are normally measured about 24 hours after the irradiation takes place, and we expect the Mn56 activty to be on the order of 10^-3 or 10^-4 uCi. For back calculated values, they would normally be on the order of 10^-1 uCi.

## Saturated Activity Calculation

To obtain the saturated activity values, you must run the python script `get_sat_act.py`
For an example, I have included the file `meas_test.txt`. This includes the foil irradiations for the 6e14 irradiation on 2/13/2019. These foils were irradiated for 27 minutes. (Note: we obtained these measurements back calculated. However, the activity measurements in this files are what we obtained after undoing the back calculation.)

The python script will calculate both the initial activities (the acitivity of the various isotopes at the end of the irradiation) and the corresponding saturated activity values. The initial activity values will be printed to the terminal, but not recorded. However, the saturated activity values will be saved to an output file.

The script uses a parser which requires two inputs, the name of the file which contains the activity measurements, and the irradiation time. You can type `python get_sat_act.py -h` to get the following script information:

------------------------------------------------------------------------

usage: `get_sat_act.py [-h] -f FILE -i IRRAD_TIME`

Give the name of the input file and the irradiation time.

optional arguments:<br/>
  `-h`, `--help`
show this help message and exit<br/>
  `-f FILE`, `--file FILE`
Name of the input file which will contain the measurements<br/>
  `-i IRRAD_TIME`, `--irrad_time IRRAD_TIME`
The length of the irradiation time, in hours<br/>

------------------------------------------------------------------------

The `-f` and `-i` arguments are required to run the script.


You can run the script over the example file by typing the following command into the terminal:

 `python get_sat_act.py -f meas_test.txt -i 0.45`

For `get_sat_act.py` the measurements in your input file must be in the following format:<br/>
foil,&nbsp; &nbsp; &nbsp; meas\_act,&nbsp; &nbsp; &nbsp; foil\_mass,&nbsp; &nbsp; &nbsp; wait\_time

Note that these script to run, these values must be delimated using a comma followed by a tab.

The variables represent the following values:<br/>
* foil:
   The name of the foil which is being activated. Note that in the case of iron, you must also specify the isotope since there are multiple isotopes which are being activated for this foil. In this script, the name of the foil is used to obtain some physics properties of the activated isotope and it's daughter isotopes which are stored in the script as python dictionaries. Note: You do not put the name of the daughter isotope (what you see in the gamma spectroscopy report).
* meas\_act:
   The activity measurement, measured in uCi, which was recorded from the gamma spectroscopy analysis
* foil\_mass:
   In the case of iron, this is the mass of the foil (in grams) which was irradiated. For the case of the CoAl wire, this is the length (in mm) of the wire. The script will then use the wire density and percent of Co in the wire to compute the mass of the Co (in grams).
* wait\_time:
   The time recorded from the gamma spectroscopy analysis. Note that if the activity values were back-calculated, two things can be done. If you input a wait time of 0, it will simply calculate the saturated activity of those values. If you input this value as the negavite of the weight\_time (for the iron in this example, this would be -26.65), the "Initial Activity" values output in the terminal window will actually be the true measured activity values (if there was no back calculation). However, know that if you put in a negative weight time, the saturated activity value will be incorrect.

After running the script, you will obtain an output file. The output file will have the same name as the input file, but with "act\_" appended to the start of the file name. This file will already be in a format which can be fed into the `normalization.py` script. However, some edits will need to be made to the output file before it can be run through the script.

#### Note, in order to make sure that the saturated values you obtained make sense, these are the average values obtained from all past rabbit system irradiations:

Fe54:  2.21E-14<br/>
Fe56:  2.78E-16<br/>
Fe58:  5.04E-12<br/>
Co:    7.46E-11<br/>

It is normal if your measured values differ from the averages by around 10-20\%

## Rabbit Flux Normalization

This script takes the saturated activity measurements obtained using `get_sat_act.py` and find a normalization of the 8-inch beam port energy spectrum which fits your measurements. It does this by applying two different normalizations. Foils which are senstive to thermal neutrons will put a normalization on the Thermal and Intermediate spectrum. Foils which are sensetive only to fission neutrons will apply a normalization to the intermediate spectrum.

If you ran the previous script on the test file, you will have the output file `act_meas_test.txt`. This file is already in the format required for the `normalization.py` script, but requires some editing. If you look at `act_meas_test.txt`, you will see that the formatting of the information is:<br/>
foil,&nbsp; &nbsp; &nbsp; sat\_act,&nbsp; &nbsp; &nbsp; \<cd or null\>,&nbsp; &nbsp; &nbsp; \<thermal or fission\>

Where the values are delimated using a comma followed by a tab (this is required for the pythong parser). The values listed represent the following things:<br/>
* foil:
   Same as for the `get_sat_act.py` script. This value is automatically entered when this file is generated.
* sat\_act:
   This is the saturated activity as calculated in the `get_sat_act.py` script. Once again, these measurements are automatically entered when this file is generated<br/>
* cd or null:
   This states whether or not the foil was encased in cadmium. If it was covered, put `cd` in this space. If not, put `null`. (Note, you can technically put anything in place of `null` and the script will interpret it the same way)
* thermal or fission:
   Whether the activation process is primarily sensetive to thermal or fission neutrons. For `Co` and `Fe58`, you would put `thermal` in this field. For `Fe54` and `Fe56` you would enter `fission` into this field.

Once the proper edits have been made to the input file, `normalize.py` can be read. Once again, the python script uses a parser. Typing `python normalize.py -h` in the terminal outputs the following help statement:

------------------------------------------------------------------------

usage: normalize.py [-h] -a ACTIVITY [-f FILE] [-p]

State name of output file you are getting your fit parameters from

optional arguments:<br/>
  `-h, --help`
show this help message and exit<br/>
  `-a ACTIVITY, --activity ACTIVITY`
Name of activity file you are using<br/>
  `-f FILE, --file FILE`
Name of file you are getting fit params from<br/>
  `-p, --plot`
Plot spectrum<br/>

------------------------------------------------------------------------

Using the `-a` option is required, and will be the name of the saturated activity file that was just entered.<br/>
The `-f` option is not reqiuired, but is used if you want to select which spectrum you wish to apply the normalization to. By default, it will normalize the spectrum using the 8-inch beam port spectrum. However, you can see the other files that you can select in the `fit_outputs/` folder. For example, if you wish to use the new 6-inch beam port spectrum, you would include `-f fit_output_new-6-inch.txt` in the command line when running the script.<br/>
Finally, the `-p` option should be included if you wish to create a plot of the normalized spectrum. Doing this will save a plot in the current directory (has the default name `normalized_spectrum.png`) as well as an image saved in the `plot/` directory. The image saved to the `plot/` directory will include the name of the activity input file in its name.


A sample version of a properly edited input file is seen in `act_test.txt`. As an example, type the following command into the terminal:

 `python normalize.py -a act_test.txt -p`

The script will then run over the saturated activity measurements specified in the file, and save plots of the spectrum. Information related to the normalization will be printed to the terminal screen and saved to an output file in the `rabbit_normalization/` folder. The output file will have the same name as the input file

### In the output files, you will get the following information:

Once you have run the previous command, you should be able to see the output file `normalization_outputs/act_test.txt`.

1. A table containing the saturated activity which was specified in the input file (meas act), the saturated activity which was calculated using the spectrum before normalization (calc act), and the ratio of the measured activity/calculated activity before normalization.
2. The average value of the average ratio of meas act/calc act for all of the foils before any normalization has been performed. This also includes the average ratios for just the foils sensetive to thermal neutrons, and the average ratio for just the foils sensetive to fission neutrons.
3. After printing out these values, the normalizations are then performed.
The output file then has a copy of the first table, but with the saturated activity values which were calculated using the now normalized spectrum.
4. The average ratio of the measured activity/calculated activity is then written again. Because the normalization is performed separately for the thermal and fission regions of the spectrum, this value might be slightly different than 1. However, it should be very close.
5. Finally, the new set of paraters which are used to define the normalized spectrum are included. This includes the following values:
   The amplitude of the termal neutron region, the amplitude of the intermediate neutron region, and the amplitude of the fission neutron region.
I also included the "connection points". These are the energies where we switch from one functional form of the spectrum to another.
