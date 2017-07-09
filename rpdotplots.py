#sometimes the GORP output contains blank lines (not sure why) - this function skips over them
def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line

#adapted from matplotlib example: add percent signs to y-axis
def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(int(y))

    # The percent symbol needs escaping in latex
    if rcParams['text.usetex'] == True:
        return s + r'$\%$'
    else:
        return s + '%'

def read_rpdot_csv(dir,filename):
	'''open the .csv files from GORP (downloaded as one row per observation). 
	returns arrays that capture the time (in seconds, starting at 0) and 
	codes associated with each button selection/deselection'''
	
	#opens the file line by line. would typically use loadtxt here, but this will run into issues
	#if a user includes commas in their comments, which are listed alongside all the other data
	f=open(dir+filename,'rU') 
	all_lines=[]
	next(f) #skip the header line
	for line in nonblank_lines(f): 	#previously just "for line in f:", this fix partly addresses blank lines problem
		if line != ',,': #ignores lines that only include commas (also related to the occasional blank lines problem)
			#print line
			all_lines.append(line.strip('\n')) #remove the newline character when reading in new lines
	f.close()
	
	#finds and removes lines that are comments, not codes
	if re.search('"',all_lines[0])==None: #most lines should be like this
		comment_indicator=re.split('-',all_lines[0],maxsplit=2)[1]
	else: #multi-line comments contain the " character - flags these as comments
		comment_indicator='Comments'	
	for i in range(1,len(all_lines)):
		if re.search('"',all_lines[i])==None:
			comment_indicator=append(comment_indicator,re.split('-',all_lines[i],maxsplit=2)[1])
		else: #fixes an bug that happens when the user hits "enter" when typing in a comment
			comment_indicator=append(comment_indicator,'Comments') #flags empty lines as being part of a comment
	#print comment_indicator
	not_a_comment=where(comment_indicator!='Comments')[0][1:]
	n_rows=len(not_a_comment)
	
	#print 'number of rows',n_rows
	
	#separates the data into the appropriate columns
	click_start_str=array([])
	click_end_str=array([])
	my_part_str=array([])
	my_act=array([])
	for i in not_a_comment:
		#print all_lines[i]
		[current_raw_codes,current_click_start_str,current_click_end_str]=re.split(',',all_lines[i]) #when saved as .txt and converted back to .csv, needed a space after the comma
		[current_part_str,temp,current_act]=re.split('-',current_raw_codes,maxsplit=2)
		click_start_str=append(click_start_str,current_click_start_str)
		click_end_str=append(click_end_str,current_click_end_str)
		my_part_str=append(my_part_str,current_part_str)
		my_act=append(my_act,current_act)
	
	click_start=zeros(n_rows)
	click_end=zeros(n_rows)
	
	#when convert_to_military is true, e.g., if the observation begins at 12PM and ends after 1PM, 
	#will add 12 to all times between 1PM and (arbitrarily) 5PM. Necessary for times not on a 24hr scale	
	init_h=re.split(':',click_start_str[0])[0]
	final_h=re.split(':',click_end_str[-1])[0]
	convert_to_military=double(final_h)-double(init_h)<0. 

	#finds the start of the whole session in order to calculate 
	#*relative* times instead of absolute times
	#for click_start and click_end
	[init_h,init_m,init_s_and_suffix]=re.split(':',click_start_str[0])
	init_s=init_s_and_suffix[:2]
	init_time=double(init_h)*3600.+double(init_m)*60.+double(init_s)

	for i in range(0,n_rows):
		[start_h,start_m,start_s_and_suffix]=re.split(':',click_start_str[i])
		start_s=start_s_and_suffix[:2]
		#start_suffix=start_s_and_suffix[-2:] #AM or PM label

		click_start[i]=double(start_h)*3600.+double(start_m)*60.+double(start_s)-init_time
		#adds 12 hours to the time just calculated, if needed
		if convert_to_military==1.:
			if double(start_h)<5.:
				click_start[i]=click_start[i]+12.*3600.
		

		[end_h,end_m,end_s_and_suffix]=re.split(':',click_end_str[i])
		end_s=end_s_and_suffix[:2]
		#end_suffix=end_s_and_suffix[-2:] #AM or PM label	
		click_end[i]=double(end_h)*3600.+double(end_m)*60.+double(end_s)-init_time
		#adds 12 hours to the time just calculated, if needed	
		if convert_to_military==1:
			if double(end_h)<5.:
				click_end[i]=click_end[i]+12.*3600.
		
		#enables data from multiple sessions to be stitched together - avoids negative times
		#if i!=0:
		#	if click_start[i]<click_start[i-1]:
				
			

	return my_part_str,my_act,click_start,click_end	

def plot_timelines(myarray,part_str,part_str_colors,act,act_colors,fignum1,fignum2,subtitle,outbase,observer,act_labels,part_str_labels):
	fig1width=16
	fig1height=2

	fig2width=fig1width
	fig2height=6
	
	fig1=figure(num=fignum1)
	clf()
	ax1=subplot(111)
	
	#creates a black background for the timeline so that gaps show up as black instead of white
	full_timeline=array([0,max(myarray[:,0])])
	ax1.fill_between(full_timeline/60.,array([1,1]),0,color='black',alpha=1) 
	
	for i in range(0,len(part_str)):
		ax1.fill_between(myarray[:,0]/60.,myarray[:,i+1],0,color=part_str_colors[i],alpha=1)
	xlim(0,myarray[-1,0]/60.)
	ylim(0,1)
	if subtitle!='':
		title('Type of Engagement: '+subtitle)
	else:
		title('Type of Engagement')
	xlabel('Time in minutes')
	ax1.set_yticklabels('')
	ax1.set_axisbelow(False)
	grid(axis='x',ls=':',linewidth=1,color='black')#color='white')
	ax1.xaxis.set_tick_params(width=1,color='black')#color='white')
	ax1.yaxis.set_tick_params(width=0)


	fig1.subplots_adjust(bottom=0.35,left=0.35,top=0.80)

	fig1.set_size_inches(fig1width,fig1height)
	savefig(outbase+'_type_of_engagement'+observer+'.png',dpi=300) 
	

	fig2=figure(num=fignum2)
	clf()
	ax2=subplot(111)
		
	for i in range(0,len(act)):
		lower_y=len(act)-(i+1)
		ax2.fill_between(myarray[:,0]/60.,myarray[:,i+1+len(part_str)]+lower_y,lower_y,color=act_colors[i])
	#draws black horizontal lines between activities (instead of having colored lines which are the default)
	for i in range(0,len(act)):
		ax2.plot(array([0,myarray[-1,0]/60.]),array([i,i]),color='black',lw=1.5)
	xlim(0,myarray[-1,0]/60.)
	ylim(0,len(act))
	if subtitle!='':
		title('Focus of Engagement: '+subtitle)
	else:
		title('Focus of Engagement')
	xlabel('Time in minutes')
	height=0.9
	act_yaxis=arange(0,len(act))+1-height
	ax2.set_yticks(act_yaxis+height/2)
	ax2.set_yticklabels(act_labels[::-1])
	#draws gridlines to help users go between the two timelines more easily
	ax2.set_axisbelow(False)
	grid(axis='x',ls=':',linewidth=1,color='black')#color='white')
	ax2.xaxis.set_tick_params(width=1,color='black')#color='white')
	ax2.yaxis.set_tick_params(width=0)
	fig2.subplots_adjust(left=0.35)

	fig2.set_size_inches(fig2width,fig2height)
	savefig(outbase+'_focus_of_engagement'+observer+'.png',dpi=300) 
	#return fig1,ax1,fig2,ax2

def parse_data(my_part_str,my_act,click_start,click_end,part_str,act):
	'''returns an array where each row is a different timestep, and the columns are: 
	time in seconds, participation structures, and activity codes. a "0" indicates a code 
	being turned off at that timestep, a "1" indicates a code being turned on at that timestep.'''

	#sets up an empty array
	n_acts=len(act) #number of activities
	n_part_str=len(part_str) #number of participation structures

	#simple time calculation. 
	total_time=click_end[-1]-click_start[0] #total time in seconds

	print 'Session length in minutes:',int(total_time/60.)
	
	#new array has enough columns to fit the time, each participation structure, and each activity code on the rows
	#and enough rows to account for each second of observation
	nrows=int(total_time)
	#print 'nrows',nrows
	#print click_start
	#print click_end
	array=zeros((nrows,1+n_acts+n_part_str),dtype=float)
	array[:,0]=arange(1,nrows+1) #first column contains the number of seconds into the session. 
	#the first column, first row is a "1", which represents seconds 0-0.999999999 (i.e., greater than or equal to 0, less than 1)
	
	for i in range(1,nrows):
		codes_on=where((click_start<i)&(click_end>=i))[0] #finds the rows with codes that are "on"
		#print shape(codes_on)
		#print codes_on
		for j in range(0,len(codes_on)):
			#locates the correct column and changes it to a 1,
			# indicating that participation structure is turned on
			#print 'j',j
			#print 'current row with codes that are on:',codes_on[j]
			#print 'current part_str:',"'"+my_part_str[codes_on[j]]+"'"
			
			#print where(my_part_str[codes_on[j]]==part_str)
			current_part_str_col=where(my_part_str[codes_on[j]]==part_str)[0][0]+1
			#print current_part_str_col 
			array[i,current_part_str_col]=1
			
			#locates the correct column and changes it to a 1, indicating that activity code is turned on
			#print 'current activity focus:',my_act[codes_on[j]]
			current_act_col=where(my_act[codes_on[j]]==act)[0][0]+1+n_part_str
			array[i,current_act_col]=1
		
	return array


def pie_and_bar_loop(my_part_str,my_act,click_start,click_end,outfile,session,part_str,act,fig_num,act_labels,part_str_labels,act_colors,part_str_colors,lw):

	act_on=click_end-click_start
	
	n_acts=len(act) #number of activities
	n_part_str=len(part_str) #number of participation structures


	#simple time calculation. 
	total_time=click_end[-1]-click_start[0]

	print 'Session length in minutes:',int(total_time/60.)

	
	#finds how long was spent in each activity
	total_act_on=zeros(n_acts) #initializes an array to record how long was spent in each activity
	for i in range(0,n_acts):
		#print act[i]
		total_act_on[i]=sum(act_on[where(my_act==act[i])[0]]) #sums how much time was spent in activity i in total
	total_act_on_percent=total_act_on/total_time*100

	#print 'activity percentages',total_act_on_percent
	print 'More than one activity focus was coded simultaneously for ~%d%% of the session'%(sum(total_act_on_percent)-100)
	#print 'summed activity percentages',sum(total_act_on_percent)
	#print ''
	subplot_num=122
	first_subplot=subplot_num
	figA=figure(num=fig_num)
	clf()
	axA=subplot(subplot_num)
			
	height=0.9
	act_yaxis=arange(0,n_acts)+1-height
	axA.barh(act_yaxis[::-1],total_act_on_percent,height=height,color=act_colors,linewidth=lw,edgecolor='white')	
	axA.set_yticks(act_yaxis+height/2)
	if subplot_num==first_subplot:
		axA.set_yticklabels(act_labels[::-1])
		xlabel('Percent of total time') #ylabel('Duration in minutes')
	else:
		axA.set_yticklabels('')
	#title(workshop+'\n'+session+': Focus of activity')
	#title(session)
	#trims edges when saving as a png, for some reason...need extra space
	#figA.subplots_adjust(left=0.29,bottom=0.11,right=0.91,top=0.93,wspace=0.27,hspace=0.20)
	figA.subplots_adjust(left=0.07,bottom=0.11,right=0.90,top=0.93,wspace=0.99,hspace=0.20)

	ylim(0,act_yaxis[-1]+1)
	xlim(0,100)

	axA.set_axisbelow(True)
	grid(axis='x',ls='-',linewidth=2,color='black')#color='white')
	axA.xaxis.set_tick_params(width=2,color='black')#color='white')
	axA.yaxis.set_tick_params(width=0)

	# Create the formatter using the function to_percent.
	formatter = FuncFormatter(to_percent)
	# Set the formatter
	figA.gca().xaxis.set_major_formatter(formatter)

	#-----------------------
	#-----------------------


	n_rows=len(my_part_str)
	total_part_str_on=zeros(n_part_str)
	part_str_start=0
	part_str_end=0
	current_pauses=0
	for i in range(0,n_rows-1):
		for j in range(0,n_part_str):
			#checks to see if this the current participation structure is what I'm looking for
			if my_part_str[i]==part_str[j]:
				if part_str_start==0:
					part_str_start=click_start[i] #sets the start time, if needed
				
				#if the next row will switch participation structures, then calculate the time 
				#spent in this structure and add to the total. reset the counter.		 
				if my_part_str[i+1]!=my_part_str[i] or i+2==n_rows:
					part_str_end=click_start[i+1] #the end of this participation structure is equivalent to the start of the next one
					total_part_str_on[j]=total_part_str_on[j]+part_str_end-part_str_start
					part_str_start=0
				

	total_part_str_on_percent=total_part_str_on/total_time*100.


	##########
	##########
	axA2=subplot(121,aspect=1)
	#print 'total part str on percent',total_part_str_on_percent
	good_part_str_ind=where(total_part_str_on_percent>1)
	wedges,texts=pie(total_part_str_on_percent[good_part_str_ind],labels=part_str_labels[good_part_str_ind],
	colors=part_str_colors[good_part_str_ind])
	
	for w in wedges:
		#w.set_linewidth(2)
		w.set_edgecolor('white')
	
	title(session)
	figwidth=18
	figheight=5
	figA.set_size_inches(figwidth,figheight)
	savefig(outfile,dpi=300) #transparent=True
	
	return total_part_str_on,total_act_on,total_time

###########################
# MAIN PROGRAM ############
###########################

from pylab import *
import re #import regular expressions to do string manipulation
import sys


def main():
	'''Usage: run rpdotplots.py inputfilename1 [inputfilename2 inputfilename3 etc.] ['combine']
	Input files should be .csv files, downloaded from the GORP interface as one row per observation.
	Updates 4/17/17: 
	- Fixed bug that occurs when the user hits "enter" when typing a comment
	- Fixed bug that occurs when the .csv file contains a blank row between each entry
	- Allowed the user to include '.csv' at the end of each filename (or not, previously the only option) without causing an error
	Updates 6/29/17
	- Added an option to combine data from multiple .csv files into one long, continuous session
	Version 1.2.1
	'''

	dir=''#can put a filepath here
	session=''#can put a title here

	if len(sys.argv)==1:
		print 'Error: incorrect number of arguments.'
		print 'Call as: "run rpdotplots_final.py inputfilename1 [inputfilename2 inputfilename3 etc.]" or "run rpdotplots_final.py inputfilename1 [inputfilename2 inputfilename3 etc.] combine"'
	elif sys.argv[-1]!='combine':	
		combinefiles='no'
		#print 'not combining files'
		#print sys.argv[-1]
		nfiles=len(sys.argv)-1
		#print nfiles
		#for i in range(0,nfiles):
		if nfiles>1:
			filenames=sys.argv[1:nfiles+1]
			#allows user to type in '.csv' at the end of each filename without causing an error
			for i in range(0,nfiles):
				if filenames[i][-4:]=='.csv':
					filenames[i]=filenames[i][:-4]
			#print filenames
		else:
			filenames=array([sys.argv[1]])
			#allows user to type in '.csv' at the end of each filename without causing an error
			if filenames[0][-4:]=='.csv':
				filenames[0]=filenames[0][:-4]
				#print filenames
		outfile_bases=array([])
		for i in range(0,nfiles):
			outfile_bases=append(outfile_bases,filenames[i])#+'.png'f [:-4]
	else:
		combinefiles='yes'
		#print sys.argv[1]
		#print sys.argv[2]
		#print sys.argv[3]
		nfiles=len(sys.argv)-2
		#print nfiles
		#for i in range(0,nfiles):
		if nfiles>1:
			print 'Script will combine input files'
			filenames=sys.argv[1:nfiles+1]
			#allows user to type in '.csv' at the end of each filename without causing an error
			for i in range(0,nfiles):
				if filenames[i][-4:]=='.csv':
					filenames[i]=filenames[i][:-4]
		else:
			print 'Error: must include more than one file if combining data.'
		outfile_bases=array([])
		for i in range(0,nfiles):
			outfile_bases=append(outfile_bases,filenames[i])#+'.png'f [:-4]

	#useful things for plots
	ion() #turns interactive plotting on (not sure why that isn't the default but this works)
	rc('font', family='sans-serif',size=16.0)
	rc('figure',facecolor='1') #color to show for background edge in interactive plotting
	rc('axes',facecolor='1')
	lw=1.5


	#part_str=array(['WL_Lecture','LG_Closed_FPQ','LG_Closed_WLQ','FP_Ind_Work','FP_Present','LG_Open_Discuss','SG_Discuss'])
	#part_str_labels=array(['WL Lecture','LG Closed FPQ','LG Closed WLQ','FP Ind Work','FP Present','LG Open Discuss','SG Discuss'])

	part_str=array(['WL_Lecture','LG_Closed_FPQ','LG_Closed_WLQ','LG_Open_Discuss','SG_Discuss','FP_Present','FP_Ind_Work'])
	part_str_labels=array(['WL Lecture','LG Closed FPQ','LG Closed WLQ','LG Open Discuss','SG Discuss','FP Present','FP Ind Work'])


	#make sure this matches the .csv file currently in use. 

	act=array(['Workshop_Instructions','Education_Research_Theory_and_Results','IS_Description_and_Purpose','WL_Simulating_IS','FP_Simulating_IS',
	'Analyzing_Simulated_IS','WL_Pre_Workshop_Experiences','FP_Pre_Workshop_Experiences','Student_Experiences','Disciplinary_Content_Knowledge',
	'Analyzing_and_Creating_Student_Tasks','Planning_for_FP_Future_Teaching'])
	#act=array(['WL_Instructions','Education_Research_Theory_and_Results','Awareness_of_IS','WL_Simulating_IS','FP_Simulating_IS',
	#'Critiquing_Simulated_IS','WL_Pre_Workshop_Experiences','FP_Pre_Workshop_Experiences','Student_Experiences','Disciplinary_Content_Knowledge',
	#'Critiquing_and_Creating_Student_Tasks','Planning_for_Future_Teaching'])

	act_labels=array(['Workshop Instructions','Education Research Theory and Results','IS Description and Purpose','WL Simulating IS','FP Simulating IS',
	'Analyzing Simulated IS','WL Pre-workshop Experiences','FP Pre-workshop Experiences','Student Experiences','Disciplinary Content Knowledge',
	'Analyzing and Creating Student Tasks','Planning for FP Future Teaching'])


	act_colors=array(['#4E0399','#7131B1','#9c69ce','#0C54D3','#1993CD','#5FC4EB','#307C24','#44AF38','#81C23B','#CCBB2D','#BD4F2A','#D77C26']) 
	part_str_colors=array(['#ECD5A2','#BD9145','#8c510a','#01665e','#5ab4ac','#ACDCD7','#E7F2F0'])#'#c7eae5','#f5f5f5']) #teal and brown tones

	nsessions=len(filenames)


	#combines multiple data chunks into one continuous "session"
	if combinefiles=='yes':
		for i in range(0,nsessions):	
			#print 'Session title:',sessions[i]
			print 'Input file:',filenames[i]+'.csv'
			#reads in the data - stores in the original chronological order, capturing code selection/deselection
			[my_part_str_current,my_act_current,click_start_current,click_end_current]=read_rpdot_csv(dir,filenames[i]+'.csv')
		
			if i==0:
				my_part_str=my_part_str_current
				my_act=my_act_current
				click_start=click_start_current
				click_end=click_end_current
			
			else:
				current_start_time=click_start[0]
				current_offset=current_start_time-previous_end_time #subtract this from current times to make a continuous dataset
				my_part_str=concatenate((my_part_str,my_part_str_current))
				my_act=concatenate((my_act,my_act_current))
				click_start=concatenate((click_start,click_start_current-current_offset))
				click_end=concatenate((click_end,click_end_current-current_offset))
		
			previous_end_time=click_end[-1]
		
	
		#makes pie charts
		print 'Output file 1:','combined_data_pie_and_bar.png'
		[total_part_str_on,total_act_on,total_time]=pie_and_bar_loop(my_part_str,my_act,click_start,click_end,
		'combined_data_pie_and_bar.png',session,part_str,act,i*3,act_labels,part_str_labels,act_colors,part_str_colors,lw)

		#creates a simple file that contains the time spent in each code
		print 'Output file 2:','combined_data_totals.csv'
		first_col=concatenate((['Total session duration (min)'],['Code name'],part_str_labels,[''],act_labels))
		second_col=concatenate(([total_time/60.],['Duration (min)'],total_part_str_on/60.,[''],total_act_on/60.))
		third_col=concatenate(([''],['Duration (frac)'],total_part_str_on/total_time,[''],total_act_on/total_time))
		myoutput=column_stack((first_col,second_col,third_col))
		savetxt('combined_data_totals.csv',myoutput,fmt='%s',delimiter=',')

		#makes timelines
		#parses the data in a different way: one row per second, and one column per code
		data_array=parse_data(my_part_str,my_act,click_start,click_end,part_str,act)
		print 'Output file 3:','combined_data_type_of_engagement.png'
		print 'Output file 4:','combined_data_focus_of_engagement.png'
		plot_timelines(data_array,part_str,part_str_colors,act,act_colors,1+i*3,2+i*3,'','combined_data','',act_labels,part_str_labels)				

	
		print '--------------------------------------------'
	else:
		for i in range(0,nsessions):	
			#print 'Session title:',sessions[i]
			print 'Input file:',filenames[i]+'.csv'
			#reads in the data - stores in the original chronological order, capturing code selection/deselection
			[my_part_str,my_act,click_start,click_end]=read_rpdot_csv(dir,filenames[i]+'.csv')
	
			#makes pie charts
			print 'Output file 1:',outfile_bases[i]+'_pie_and_bar.png'
			[total_part_str_on,total_act_on,total_time]=pie_and_bar_loop(my_part_str,my_act,click_start,click_end,
			outfile_bases[i]+'_pie_and_bar.png',session,part_str,act,i*3,act_labels,part_str_labels,act_colors,part_str_colors,lw)
	
			#creates a simple file that contains the time spent in each code
			print 'Output file 2:',outfile_bases[i]+'_totals.csv'
			first_col=concatenate((['Total session duration (min)'],['Code name'],part_str_labels,[''],act_labels))
			second_col=concatenate(([total_time/60.],['Duration (min)'],total_part_str_on/60.,[''],total_act_on/60.))
			third_col=concatenate(([''],['Duration (frac)'],total_part_str_on/total_time,[''],total_act_on/total_time))
			myoutput=column_stack((first_col,second_col,third_col))
			savetxt(outfile_bases[i]+'_totals.csv',myoutput,fmt='%s',delimiter=',')
	
			#makes timelines
			#parses the data in a different way: one row per second, and one column per code
			data_array=parse_data(my_part_str,my_act,click_start,click_end,part_str,act)
			print 'Output file 3:',outfile_bases[i]+'_type_of_engagement.png'
			print 'Output file 4:',outfile_bases[i]+'_focus_of_engagement.png'
			plot_timelines(data_array,part_str,part_str_colors,act,act_colors,1+i*3,2+i*3,'',outfile_bases[i],'',act_labels,part_str_labels)				
	
		
			print '--------------------------------------------'

if __name__ == "__main__":
    main()
