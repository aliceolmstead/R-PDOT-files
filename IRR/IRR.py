def read_rpdot_csv(dir,filename):
	'''open the .csv files from GORP (downloaded as one row per observation). 
	returns arrays that capture the time (in seconds, starting at 0) and 
	codes associated with each button selection/deselection'''
	
	#opens the file line by line. would typically use loadtxt here, but this will run into issues
	#if a user includes commas in their comments, which are listed alongside all the other data
	f=open(dir+filename,'rU') 
	all_lines=[]
	next(f) #skip the header line
	for line in f:
		all_lines.append(line.strip('\n')) #remove the newline character when reading in new lines
	f.close()
	
	#finds and removes lines that are comments, not codes
	comment_indicator=re.split('-',all_lines[0],maxsplit=2)[1]
	for i in range(1,len(all_lines)):
		comment_indicator=append(comment_indicator,re.split('-',all_lines[i],maxsplit=2)[1])
	not_a_comment=where(comment_indicator!='Comments')[0][1:]
	n_rows=len(not_a_comment)
	
	#separates the data into the appropriate columns
	click_start_str=array([])
	click_end_str=array([])
	my_part_str=array([])
	my_act=array([])
	for i in not_a_comment:
		#when downloading files directly from the GORP website, there is a space after the comma,
		#but when converting from .txt to .csv, the space is removed
		if len(re.split(', ',all_lines[i]))==1:
			[current_raw_codes,current_click_start_str,current_click_end_str]=re.split(',',all_lines[i])
		else:
			[current_raw_codes,current_click_start_str,current_click_end_str]=re.split(', ',all_lines[i])
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

	return my_part_str,my_act,click_start,click_end	

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
			#print 'current part_str:',my_part_str[codes_on[j]]
			#print where(my_part_str[codes_on[j]]==part_str)
			current_part_str_col=where(my_part_str[codes_on[j]]==part_str)[0][0]+1
			#print current_part_str_col 
			array[i,current_part_str_col]=1
			
			#locates the correct column and changes it to a 1, indicating that activity code is turned on
			#print 'current activity focus:',my_act[codes_on[j]]
			current_act_col=where(my_act[codes_on[j]]==act)[0][0]+1+n_part_str
			array[i,current_act_col]=1
		
	return array
	
def plot_timelines(myarray,part_str,part_str_colors,act,act_colors,fignum1,fignum2,subtitle,outbase,observer):


	fig1width=16
	fig1height=2

	fig2width=fig1width
	fig2height=6
	
	fig1=figure(num=fignum1)
	clf()
	ax1=subplot(111)

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
	fig1.subplots_adjust(bottom=0.35,left=0.35,top=0.80)

	fig1.set_size_inches(fig1width,fig1height)
	current_outfile=outbase+'_type_of_engagement_'+observer+'.png'
	savefig(current_outfile,dpi=300) 
	print current_outfile

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
	fig2.subplots_adjust(left=0.35)

	fig2.set_size_inches(fig2width,fig2height)
	current_outfile=outbase+'_focus_of_engagement_'+observer+'.png'
	savefig(current_outfile,dpi=300) 
	print current_outfile
	#return fig1,ax1,fig2,ax2


def reduce_arrays(array1,array2):
	'''returns "reduced" arrays that omit data x seconds before and after code switches, changing
	those 1s to 0s such that it looked like no codes were selected at those times
	also returns the total number of observations omitted for each code, which can be subtracted from totals where needed
	'''
	
	x=int(2) #ignore 2 seconds before and after the start of codes
	#finds values to ignore before transitions
	#make a copy of array1 where all observations are shifted x seconds earlier
	array1_shifted_up=zeros(shape(array1))
	array1_shifted_up[:-1*x,1:]=array1[x:,1:]
	#compare the array to the actual observation: make an array where 0 indicates disagreement 
	#with the original array and 1 indicates agreement. 
	ignore_before1=1.-abs(array1[:,1:]-array1_shifted_up[:,1:])

	#make a copy of array1 where all observations are shifted x seconds later
	array1_shifted_down=zeros(shape(array1))
	array1_shifted_down[x:,1:]=array1[:-1*x,1:]
	#compare the array to the actual observation: make an array where 0 indicates disagreement 
	#with the original array and 1 indicates agreement. 
	ignore_after1=1.-abs(array1[:,1:]-array1_shifted_down[:,1:])

	#make a copy of array1 where all observations are shifted x seconds earlier
	array2_shifted_up=zeros(shape(array2))
	array2_shifted_up[:-1*x,1:]=array2[x:,1:]
	#compare the array to the actual observation: make an array where 0 indicates disagreement 
	#with the original array and 1 indicates agreement. 
	ignore_before2=1.-abs(array2[:,1:]-array2_shifted_up[:,1:])

	#make a copy of array1 where all observations are shifted x seconds later
	array2_shifted_down=zeros(shape(array2))
	array2_shifted_down[x:,1:]=array2[:-1*x,1:]
	#compare the array to the actual observation: make an array where 0 indicates disagreement 
	#with the original array and 1 indicates agreement. 
	ignore_after2=1.-abs(array2[:,1:]-array2_shifted_down[:,1:])


	#creates a single array where 0 indicates any disagreement with either original array and 
	#1 indicates all agreement, effectively changing all data x seconds before and after a code switch to 0
	ignore_array=ignore_before1*ignore_before2*ignore_after1*ignore_after2
	#modifies the two arrays. ignored observations now show up as both observers coding 0, i.e., 
	#it will look like they agree that the code is not selected.
	array1[:,1:]=array1[:,1:]*ignore_array
	array2[:,1:]=array2[:,1:]*ignore_array
	#sum up number of observations omitted for each code, subtract this from totals where needed
	n_ignore=sum(1-ignore_array,axis=0) 

	return array1,array2,n_ignore

def calc_IRR(array1,array2,n_ignore,part_str_ind,act_ind,part_str_labels,act_labels,observer1,observer2,outfile):
	
	T=calc_Jaccard(array1,array2,n_ignore)

	part_str_kappa=calc_single_kappa(array1[:,part_str_ind],array2[:,part_str_ind])

	[act_kappas,good_act_kappas]=calc_kappas(array1[:,act_ind],array2[:,act_ind],n_ignore[act_ind-1])

	calc_totals_and_save_all(array1,array2,part_str_labels,act_labels,part_str_ind,act_ind,
	T,part_str_kappa,act_kappas,outfile)

	return

def calc_Jaccard(array1,array2,n_ignore):
	'''calculates Jaccard similarity scores for each code individually'''

	#n_c is a vector containing the number of time intervals where observers 
	#marked a code in the same way (selected or not)
	agreement_array=(array1[:,1:]==array2[:,1:])*1
	n_c=sum(agreement_array,axis=0)-n_ignore

	#calculates n_a, the number of time intervals marked the same for both observers (n_c), 
	#plus the number of time intervals where observer 1 selected a code when observer 2 did not
	difference_array1=array1[:,1:]-array2[:,1:]
	difference_array1[where(difference_array1<0)]=0
	difference_vector1=sum(difference_array1,axis=0)
	n_a=n_c+difference_vector1

	#calculates n_b, the number of time intervals marked the same for both observers (n_c), 
	#plus the number of time intervals where observer 2 selected a code when observer 1 did not
	difference_array2=array2[:,1:]-array1[:,1:]
	difference_array2[where(difference_array2<0)]=0
	difference_vector2=sum(difference_array2,axis=0)
	n_b=n_c+difference_vector2			
	
	
	#calculates the Jaccard similarity score for each code
	T=n_c/(n_a+n_b-n_c)
	
	return T

def calc_single_kappa(array1,array2):
	'''calculates Cohen's kappa for a set of exclusive categorical items, in this case, the 
	participation structure (type of engagement) codes'''
	
	total=sum(array1) #total number of observations made by each observer - code is selected
	
	bothselected_array=array1*array2
	bothselected_vector=sum(bothselected_array,axis=0)
	bothselected_total=sum(bothselected_vector)

	p_o=bothselected_total/total #observed proportionate agreement
	
	codefracs1=sum(array1,axis=0)/total #fraction of time each code was selected for observer 1
	codefracs2=sum(array2,axis=0)/total #fraction of time each code was selected for observer 2
	
	#print codefracs1
	#print codefracs2
	
	rand_agree_probs=codefracs1*codefracs2 #vector containing the probability of random agreement for each code
	p_e=sum(rand_agree_probs) #probability of random agreement
	
	kappa=(p_o-p_e)/(1.-p_e)
	
	return kappa

def calc_kappas(array1,array2,n_ignore):
	'''calculates many kappas, one for each code. looks at whether codes were selected OR NOT SELECTED
	at a given time (where counting whether or not the code was NOT selected is different from calculating a single kappa
	for exclusive codes)'''

	total=shape(array1)[0]-n_ignore #total number of observations per code to count for each observer
	
	#n_c is a vector containing the number of time intervals where observers 
	#marked a code in the same way (selected or not)
	agreement_array=(array1==array2)*1
	n_c=sum(agreement_array,axis=0)-n_ignore #subtracts the number of times when the arrays
	#are the same because they were manually zeroed out
	
	p_o=n_c/total #vector containing the observed proportionate agreement for each code
	
	#sums the number of times each code was selected for each observer, divides by total
	#number of observations being counted
	fracyes1=sum(array1,axis=0)/total
	fracyes2=sum(array2,axis=0)/total
	
	#inverts the arrays: 0 -> 1 and 1->0, sums the number of times each code was now NOT selected,
	#subtracts the appropriate number of artificial zeros
	fracno1=(sum(1.-array1,axis=0)-n_ignore)/total
	fracno2=(sum(1.-array2,axis=0)-n_ignore)/total
		
	p_e=fracyes1*fracyes2+fracno1*fracno2 #vector containing probabilities of random agreement
	
	kappas=zeros(shape(array1)[1],dtype=double)
	
	good=where(fracyes1*fracyes2*fracno1*fracno2!=0)[0] #none of these values can be zero. 
	#if there's no variation for either observer, then kappa is 0
		
	kappas[good]=(p_o[good]-p_e[good])/(1.-p_e[good])
	
	return kappas,good
	
def calc_totals_and_save_all(array1,array2,part_str_labels,act_labels,part_str_ind,act_ind,T,part_str_kappa,act_kappas,outfile):
	#calculates total duration spent in each code, for each observer, in minutes and as a fraction of the total time in the session
	total_duration=double(shape(array1)[0])/60.
	n_part_str=len(part_str_labels)
	part_str_totals_1=zeros(n_part_str,dtype=double)
	part_str_totals_2=zeros(n_part_str,dtype=double)
	for i in range(0,n_part_str):
		part_str_totals_1=sum(array1[:,part_str_ind],axis=0)/60.
		part_str_totals_2=sum(array2[:,part_str_ind],axis=0)/60.
		part_str_totals_average=average((part_str_totals_1,part_str_totals_2),axis=0)
	
	n_act=len(act_labels)	
	act_totals_1=zeros(n_act,dtype=double)
	act_totals_2=zeros(n_act,dtype=double)
	for i in range(0,n_act):
		act_totals_1=sum(array1[:,act_ind],axis=0)/60.
		act_totals_2=sum(array2[:,act_ind],axis=0)/60.
		act_totals_average=average((act_totals_1,act_totals_2),axis=0)
		
	
	part_str_totals_frac_1=part_str_totals_1/total_duration
	part_str_totals_frac_2=part_str_totals_2/total_duration
	part_str_totals_frac_average=part_str_totals_average/total_duration
	act_totals_frac_1=act_totals_1/total_duration
	act_totals_frac_2=act_totals_2/total_duration
	act_totals_frac_average=act_totals_average/total_duration

	
	#combines all data into a single array and produces a text file
	all_labels=concatenate((['Code name'],part_str_labels,act_labels))
	#all_totals_1=concatenate((['Total duration '+observer1+' (min)'],part_str_totals_1,act_totals_1))
	#all_totals_2=concatenate((['Total duration '+observer2+' (min)'],part_str_totals_2,act_totals_2))
	all_totals_average=concatenate((['Average duration (min)'],part_str_totals_average,act_totals_average))
	#all_totals_frac_1=concatenate((['Total duration '+observer1+' (frac of total)'],part_str_totals_frac_1,act_totals_frac_1))
	#all_totals_frac_2=concatenate((['Total duration '+observer2+' (frac of total)'],part_str_totals_frac_2,act_totals_frac_2))
	all_totals_frac_average=concatenate((['Average duration (fraction of total)'],part_str_totals_frac_average,act_totals_frac_average))
	all_T=concatenate((['Jaccard Score'],T))
	all_kappas=concatenate((['Kappa'],[part_str_kappa]*n_part_str,act_kappas))
	#myoutput=column_stack((all_labels,all_totals_1,all_totals_2,all_totals_frac_1,all_totals_frac_2,all_T,all_kappas))
	myoutput1=column_stack((all_labels,all_totals_average,all_totals_frac_average,all_T,all_kappas))
	#myoutput1=column_stack((all_labels,all_totals_frac_1,all_totals_frac_2,all_T,all_kappas))
	
	
	ncolumns=5
	firstrow=concatenate((['Total session duration (min)'],[total_duration],['']*(ncolumns-2)))
	middlerow=['']*ncolumns
	myoutput=row_stack((firstrow,myoutput1[:n_part_str+1,:],middlerow,myoutput1[n_part_str+1:,:]))
	
	savetxt(outfile,myoutput,fmt='%s',delimiter=',')
	
	return	


###########################
# MAIN PROGRAM ############
###########################
'''usage: run IRR_vX.py observer1 observer2 sessionID1 [sessionID2 sessionID3 etc.]'''
#this version combines multiple sessions to get overall measurements of IRR
#this version accepts .csv files (instead of .txt files)

from pylab import *
import re #import regular expressions to do string manipulation
import sys

if len(sys.argv)<4:
 	print 'Error: incorrect number of arguments.'
 	print 'Call as: run IRR_v4.py observer1 observer2 sessionID1 [sessionID2 sessionID3 etc.]'
 	print "For example: run IRR_v4.py 'AO' 'CT' 'LearnerCenteredTeaching_June2015_clip1'"
else:
	observer1=sys.argv[1]
	observer2=sys.argv[2]
	nfiles=len(sys.argv)-3
	#print observer1
	#print nfiles
	#for i in range(0,nfiles):
	if nfiles>1:
		sessionIDs=sys.argv[3:nfiles+3]
	else:
		sessionIDs=array([sys.argv[3]])
	filenames1=array([])
	filenames2=array([])
	for i in range(0,nfiles):
		filenames1=append(filenames1,sessionIDs[i]+'_'+observer1+'.csv')
		filenames2=append(filenames2,sessionIDs[i]+'_'+observer2+'.csv')


#useful things for plots
#ion() #turns interactive plotting on (not sure why that isn't the default but this works)
rc('font', family='sans-serif',size=16.0)
rc('figure',facecolor='1') #color to show for background edge in interactive plotting
rc('axes',facecolor='1')
lw=1.5


act_colors=array(['#4E0399','#7131B1','#9c69ce','#0C54D3','#1993CD','#5FC4EB','#307C24',
'#44AF38','#81C23B','#CCBB2D','#BD4F2A','#D77C26']) 
part_str_colors=array(['#ECD5A2','#BD9145','#8c510a','#01665e','#5ab4ac','#ACDCD7','#E7F2F0'])#'#c7eae5','#f5f5f5']) #teal and brown tones

#assumes input files are in the current directory (could modify this)
dir=''
nsessions=len(filenames1)

#make sure this matches the .txt file currently in use. 
part_str=array(['WL_Lecture','LG_Closed_FPQ','LG_Closed_WLQ','LG_Open_Discuss','SG_Discuss','FP_Ind_Work','FP_Present'])
part_str_labels=array(['WL Lecture','LG Closed FPQ','LG Closed WLQ','LG Open Discuss','SG Discuss','FP Ind Work','FP Present'])

act=array(['Workshop_Instructions','Education_Research_Theory_and_Results','IS_Description_and_Purpose','WL_Simulating_IS','FP_Simulating_IS',
'Analyzing_Simulated_IS','WL_Pre_Workshop_Experiences','FP_Pre_Workshop_Experiences','Student_Experiences','Disciplinary_Content_Knowledge',
'Analyzing_and_Creating_Student_Tasks','Planning_for_FP_Future_Teaching'])
act_labels=array(['Workshop Instructions','Education Research Theory and Results','IS Description and Purpose','WL Simulating IS','FP Simulating IS',
'Analyzing Simulated IS','WL Pre-workshop Experiences','FP Pre-workshop Experiences','Student Experiences','Disciplinary Content Knowledge',
'Analyzing and Creating Student Tasks','Planning for FP Future Teaching'])

n_part_str=len(part_str)
part_str_ind=arange(0,n_part_str)+1 #participation structure columns in the parsed arrays
n_act=len(act)
act_ind=arange(n_part_str,n_part_str+n_act)+1 #activity focus columns in the parsed arrays

for i in range(0,nsessions):
	print '-----------------------------------------------------------------'
	#print 'Workshop:',workshop
	print 'Input file 1:',filenames1[i]
	[my_part_str1,my_act1,click_start1,click_end1]=read_rpdot_csv(dir,filenames1[i])
	current_array1=parse_data(my_part_str1,my_act1,click_start1,click_end1,part_str,act)
	print 'Input file 2:',filenames2[i]
	[my_part_str2,my_act2,click_start2,click_end2]=read_rpdot_csv(dir,filenames2[i])
	current_array2=parse_data(my_part_str2,my_act2,click_start2,click_end2,part_str,act)

	#makes the arrays the same length. 
	#assumes the start times are the same, so ignores the last few rows of the longer array.
	if len(current_array1)>len(current_array2):
		current_array1=current_array1[:len(current_array2),:]
	if len(current_array2)>len(current_array1):
		current_array2=current_array2[:len(current_array1),:]
	
	#plots timelines
	print ''
	print 'Timeline plots created and saved as:'
	plot_timelines(current_array1,part_str,part_str_colors,act,act_colors,1+i*4,2+i*4,'Session %d, '%(i+1)+observer1,sessionIDs[i],observer1)
	plot_timelines(current_array2,part_str,part_str_colors,act,act_colors,3+i*4,4+i*4,'Session %d, '%(i+1)+observer2,sessionIDs[i],observer2)

	#performs calculations for IRR
	#removes values x seconds before and after the start of codes, and returns a vector containing how
	#many times each code was ignored
	[current_array1,current_array2,current_n_ignore]=reduce_arrays(current_array1,current_array2)

	#print 'Session %d Similarity and Reliability Results'%(i+1)
	current_outfile=(filenames1[i][:-6]+'IRR.csv')
	calc_IRR(current_array1,current_array2,current_n_ignore,part_str_ind,act_ind,part_str_labels,act_labels,observer1,observer2,current_outfile)
	print ''
	print 'IRR results saved in '+current_outfile
	print ''
	
	if i==0:
		all_array1=current_array1
		all_array2=current_array2
		all_n_ignore=current_n_ignore
	else:
		all_array1=append(all_array1,current_array1,axis=0)
		all_array2=append(all_array2,current_array2,axis=0)
		all_n_ignore=all_n_ignore+current_n_ignore


#print '-----------------------------------------------------------------'
#print 'Similarity and Reliability Results: All Sessions Combined'
if nsessions>1:
	calc_IRR(all_array1,all_array2,all_n_ignore,part_str_ind,act_ind,part_str_labels,act_labels,observer1,observer2,'combinedsessionsIRR.csv')
	print 'Combined IRR results for all sessions saved in '+'combinedsessionsIRR.csv'