README

This is the README file for creating R-PDOT plots and calculating inter-rater reliability between two observers. Note that this has only been tested on macs, though in theory it would work on any computer with Python installed. The built-in software on macs seems to work fine — installing a different version of python or related packages has not been necessary, but we have not done extensive testing around this issue. 

WHAT IS IN THIS REPOSITORY

README - this file

rpdotplots.py - a python script that creates visualizations of data from one or more sessions, including a pie chart showing the type-of-engagement, a bar chart showing focus-of-engagement, and color-coded timelines

SessionC.csv - example data for creating visualizations, specifically the data from “Session C” in our R-PDOT development paper

IRR - a subdirectory containing files relevant to calculating inter-rater reliability (IRR): 
	IRR.py - a python script that calculates the inter-rater reliability between two observers measured by the Jaccard similarity score and Cohen’s kappa for one or more sessions (separately and combined), and creates timeline plots for quick visual comparison
	Clip1_AO.csv - example R-PDOT data from a ~20-minute session excerpt, coded by the observer with initials ‘AO’
	Clip1_CT.csv - example R-PDOT data from the same 20-minute session excerpt, coded by the observer with initials ’CT’
	Clip2_AO.csv - example data from a second ~20-minute session excerpt, coded by ‘AO’
	Clip2_CT.csv - example data from the second ~20-minute session excerpt, coded by ‘CT’


CREATING VISUALIZATIONS

Download files from git.

Open a Terminal and navigate to the appropriate directory. I moved my folder is on the desktop, so I would type:

cd Desktop/R-PDOT-files-master

in the Terminal window. You can type “ls” to verify that the files listed above are in the directory and that you have navigated to the correct location.

In the main directory, type

python rpdotplots.py SessionC

When you type “ls” again, you should see three R-PDOT plots (SessionC_type_of_engagement.png, SessionC_focus_of_engagement.png, and SessionC_pie_and_bar.png) and a new .csv file called SessionC_totals.csv, which has the exact percentages represented in the pie and bar charts.

If you type:
open *png

all of the images will open in Preview.

If you wish to plot multiple datasets quickly, you can include multiple file names in the python command, e.g.,

python rpdotplots.py SessionC OtherSession AnotherSession

which will create three plots and a .csv file for each session using the same naming convention as above.

*UPDATE* 
In the latest version (1.2), users can also choose to combine data from multiple workshop sessions into one long session by adding the keyword ‘combine’ at the end of the command. For example, 

python rpdotplots.py SessionC SessionD  combine

will create files that starting with ‘combined_data’ and represent data from Sessions C and D as one continuous session.


CALCULATING INTER-RATER RELIABILITY
To use the inter-rater reliability script, navigate to the IRR subdirectory (cd IRR), then test the script by typing:

python IRR.py AO CT Clip1 Clip2

This will create several files. Two timeline visualizations—-one showing focus-of-engagement and one showing type-of-engagement—-will be created for each input .csv file. Looking back and forth between timelines can help users troubleshoot challenges and resolve inconsistencies between their interpretations of the R-PDOT codes. 

This script also outputs formal IRR metrics as .csv files, including the average length of time each observer selected each code in minutes and as a fraction of the total time, the Jaccard similarity score, and Cohen’s kappa. (Note that a single value of kappa is calculated for all the focus-of-engagement codes taken together, and this same value is listed in each focus-of-engagement row in the .csv file.) A .csv file with these metrics is created for each session excerpt separately, e.g., Clip1_IRR.csv. A file called combinedsessionsIRR.csv contains the cumulative IRR results for all of the input files taken together.

Any number of files can be appended to the end of the IRR command, e.g.,

python IRR.py AO CT Clip1 Clip2 Clip3 Clip4

It is also possible to run this script with only one data pair, e.g.,

python IRR.py AO CT Clip1


COLLECTING AND DOWNLOADING NEW DATA FROM GORP
The R-PDOT interface is available to any GORP user. The GORP website is gorp.ucdavis.edu. You need approval from an “administrator” at your home institution to make an account. Alternatively, Chandra Turpen and I (Alice) can approve users for the “University of Maryland - Turpen Research Group”. 

If/when you collect your own data, download it as “one row per observation” and follow the same procedure as outlined for the sample data above. 

For calculating inter-rater reliability, files should be named as NameofClipOrSession_ObserverInitials.csv.


Please contact me (Alice Olmstead--alice.olmstead@wmich.edu) with questions or suggestions.

Last updated 6.29.17.


