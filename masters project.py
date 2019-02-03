# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns


# Need to pull in the subject data from the Excel file and then set the
# index to be the subject ID.

Subjects = pd.read_excel(r"C:\Users\smusio2\Research project data\Test model Study lab values revised.xlsx", 'Cleaned Subject Values')
Subjects.set_index('subject_id', inplace=True)

# Create a dictionary that lets us look up the stats based on subject ID.
Subj_stats = Subjects.to_dict(orient='index')

# Read in the initial data model with basic indexing (this was more functional
# from a data analysis and iteration/comparison standpoint)
data_model = pd.read_excel(r"C:\Users\smusio2\Research project data\Test model Study lab values revised.xlsx", 'Data Model')

# Need to loop through data_model and compare previous row to current row. If current
# row elements are the same as the previous row elements, do nothing. If they are different,
# then need to add tube volume to new column called draw_volume.

#line1 = data_model.iloc[0, 0]
#line2 = data_model.iloc[1, [0, 1, 2, 4, 6]]

# create the draw volume list
draw_volume = []
subj_vol = []

# iterate through the data model
for i in range(0, len(data_model)):
#create a counter for the subject that we're on for the nested lists
    if i == 0:
        subj_vol.append(data_model.iloc[i, 6])
        
    elif i == len(data_model)-1:
        draw_volume.append(subj_vol)
        Subj_stats[data_model.iloc[i, 0]]['discharge'] = data_model.iloc[i, 1]
    else:
# check to see if we're on the same subjects    
        if data_model.iloc[i, 0] == data_model.iloc[i-1, 0]:
            #subj_vol = []
            # load two rows of data into strings for comparison
            row1 = data_model.iloc[i, [1, 2, 5, 7]].to_string()
            row2 = data_model.iloc[i-1, [1, 2, 5, 7]].to_string()
            # check if the strings are the same
            if row1 == row2:
                # if draw volume is not empty and the rows are equal, add the last value in draw volume onto the list
                if not subj_vol:
                    subj_vol.append(data_model.iloc[i, 6])
                    
                # if we have an empty list, add the draw volume to the list
                else:                
                   subj_vol.append(subj_vol[-1]) 
            # if the two strings are NOT equal, add the last draw volume and that row's draw volume to get the cumulative draw volume
            else:           
               add_volume = subj_vol[-1] + data_model.iloc[i, 6]
               subj_vol.append(add_volume)
        # if we move on to the next subject, start with the first draw volume
        else:
            Subj_stats[data_model.iloc[i-1, 0]]['discharge'] = data_model.iloc[i-1, 1]
            draw_volume.append(subj_vol)
            subj_vol = []
            subj_vol.append(data_model.iloc[i, 6])
            #draw_volume.append(data_model.iloc[i, 6])
        

# 1. Need to get the maximum total draw volume for each patient

pt_vol = []
# iterate through draw_volume list
for volumes in draw_volume:
    # assign nested list to numpy array
    vol_arr = np.array(volumes)
    # assign the maximum vol as total draw volume
    tot_vol = np.max(vol_arr)
    #append the total draw volume to a list to iterate through for each subject
    pt_vol.append(tot_vol)

# 2. Add each draw volume to the dictionary Subj_stats    
for i in range(0, len(pt_vol)):
    # use each index to get the subject id and then append the draw volume to the subj_stats dictionary
    Subj_stats[Subjects.index[i]]['draw_volume'] = pt_vol[i]

 # create the Hgb value list
hgb_values = []
subj_hgb = [] 

for i in range(0, len(data_model)):
#create a counter for the subject that we're on for the nested lists
    if i == 0:
        if pd.isnull(data_model.iloc[i, 4]) == False:
            subj_hgb.append(data_model.iloc[i, 4])
    elif i == len(data_model)-1:
        hgb_values.append(subj_hgb)
    else:
# check to see if we're on the same subjects    
        if data_model.iloc[i, 0] == data_model.iloc[i-1, 0]:
            if pd.isnull(data_model.iloc[i, 4]) == False:
                subj_hgb.append(data_model.iloc[i, 4])
        # if we move on to the next subject, start with the first hgb value
        else:
           hgb_values.append(subj_hgb)
           subj_hgb = [] 
           
for i in range(0, len(hgb_values)):
    Subj_stats[Subjects.index[i]]['first_hgb'] = hgb_values[i][0]
    Subj_stats[Subjects.index[i]]['last_hgb'] = hgb_values[i][-1]
    
    
# next need to run the calculations for each subject: nursing and Lyons
for key in Subj_stats:
    if Subj_stats[key]['gender'] == 'f':
        # calculate the nursing estimated value as 'control value'
        Subj_stats[key]['control value'] = Subj_stats[key]['first_hgb'] * ((((Subj_stats[key]['weight (lbs)'] * 0.4536) * 61.9) - Subj_stats[key]['draw_volume'])/((Subj_stats[key]['weight (lbs)'] * 0.4536) * 61.9))
    else:
        Subj_stats[key]['control value'] = Subj_stats[key]['first_hgb'] * ((((Subj_stats[key]['weight (lbs)'] * 0.4536) * 62.4) - Subj_stats[key]['draw_volume'])/((Subj_stats[key]['weight (lbs)'] * 0.4536) * 62.4))
        

# calculate the blood volume for each subject 
for key in Subj_stats:
    if Subj_stats[key]['gender'] == 'f':
        # calculate the blood volume for each subject
        Subj_stats[key]['blood volume'] = (Subj_stats[key]['weight (lbs)'] * 0.4536) * 61.9
    else:
        Subj_stats[key]['blood volume'] = (Subj_stats[key]['weight (lbs)'] * 0.4536) * 62.4

# calculate the total time in days of the admission        
for key in Subj_stats:
    Subj_stats[key]['days'] = (pd.Timestamp.date(Subj_stats[key]['discharge']) - pd.Timestamp.date(Subj_stats[key]['admit'])).days
    if Subj_stats[key]['days'] == 0:
        Subj_stats[key]['days'] = 1
        
 # above code works for what we need
k2 = 0.01155

for key in Subj_stats:
    k1 = (-np.log((Subj_stats[key]['blood volume'] - Subj_stats[key]['draw_volume'])/Subj_stats[key]['blood volume']))/Subj_stats[key]['days']
    k3 = ((Subj_stats[key]['first_hgb']) * ((0.5 * Subj_stats[key]['blood volume'])/60))/Subj_stats[key]['blood volume']
    Lyons_a = -(k1 + k2) * Subj_stats[key]['days']
    Subj_stats[key]['Lyons value'] = (Subj_stats[key]['first_hgb'] * np.exp(Lyons_a)) + ((1 - np.exp(Lyons_a)) * (k3/(k1 + k2)))
    
    
for key in Subj_stats:
    if Subj_stats[key]['gender']=='f' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['Lyons value'] > 12.2:
            Subj_stats[key]['Lyons alert'] = 'None'
        elif Subj_stats[key]['Lyons value'] >= 11.1:
            Subj_stats[key]['Lyons alert'] = 'Mild'
        elif Subj_stats[key]['Lyons value'] >= 9.0:
            Subj_stats[key]['Lyons alert'] = 'Moderate'
        else:
            Subj_stats[key]['Lyons alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='f' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['Lyons value'] > 11.5:
            Subj_stats[key]['Lyons alert'] = 'None'
        elif Subj_stats[key]['Lyons value'] >= 10.6:
            Subj_stats[key]['Lyons alert'] = 'Mild'
        elif Subj_stats[key]['Lyons value'] >= 9.0:
            Subj_stats[key]['Lyons alert'] = 'Moderate'
        else:
            Subj_stats[key]['Lyons alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['Lyons value'] > 13.2:
                Subj_stats[key]['Lyons alert'] = 'None'
            elif Subj_stats[key]['Lyons value'] >= 11.1:
                Subj_stats[key]['Lyons alert'] = 'Mild'
            elif Subj_stats[key]['Lyons value'] >= 9.0:
                Subj_stats[key]['Lyons alert'] = 'Moderate'
            else:
                Subj_stats[key]['Lyons alert'] = 'Severe'
        else:
            if Subj_stats[key]['Lyons value'] > 13.7:
                Subj_stats[key]['Lyons alert'] = 'None'
            elif Subj_stats[key]['Lyons value'] >= 11.1:
                Subj_stats[key]['Lyons alert'] = 'Mild'
            elif Subj_stats[key]['Lyons value'] >= 9.0:
                Subj_stats[key]['Lyons alert'] = 'Moderate'
            else:
                Subj_stats[key]['Lyons alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['Lyons value'] > 12.7:
                Subj_stats[key]['Lyons alert'] = 'None'
            elif Subj_stats[key]['Lyons value'] >= 11.1:
                Subj_stats[key]['Lyons alert'] = 'Mild'
            elif Subj_stats[key]['Lyons value'] >= 9.0:
                Subj_stats[key]['Lyons alert'] = 'Moderate'
            else:
                Subj_stats[key]['Lyons alert'] = 'Severe'
        else:
            if Subj_stats[key]['Lyons value'] > 12.9:
                Subj_stats[key]['Lyons alert'] = 'None'
            elif Subj_stats[key]['Lyons value'] >= 11.1:
                Subj_stats[key]['Lyons alert'] = 'Mild'
            elif Subj_stats[key]['Lyons value'] >= 9.0:
                Subj_stats[key]['Lyons alert'] = 'Moderate'
            else:
                Subj_stats[key]['Lyons alert'] = 'Severe'
                

for key in Subj_stats:
    if Subj_stats[key]['race'] in ['other', 'unk', 'refused']:
        Subj_stats[key]['control alert'] = 'N/A'
        Subj_stats[key]['Lyons alert'] = 'N/A'
        Subj_stats[key]['WHO actual alert'] = 'N/A'
    elif Subj_stats[key]['gender']=='f' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['control value'] > 12.2:
            Subj_stats[key]['control alert'] = 'None'
        elif Subj_stats[key]['control value'] >= 11.1:
            Subj_stats[key]['control alert'] = 'Mild'
        elif Subj_stats[key]['control value'] >= 9.0:
            Subj_stats[key]['control alert'] = 'Moderate'
        else:
            Subj_stats[key]['control alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='f' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['control value'] > 11.5:
            Subj_stats[key]['control alert'] = 'None'
        elif Subj_stats[key]['control value'] >= 10.6:
            Subj_stats[key]['control alert'] = 'Mild'
        elif Subj_stats[key]['control value'] >= 9.0:
            Subj_stats[key]['control alert'] = 'Moderate'
        else:
            Subj_stats[key]['control alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['control value'] > 13.2:
                Subj_stats[key]['control alert'] = 'None'
            elif Subj_stats[key]['control value'] >= 11.1:
                Subj_stats[key]['control alert'] = 'Mild'
            elif Subj_stats[key]['control value'] >= 9.0:
                Subj_stats[key]['control alert'] = 'Moderate'
            else:
                Subj_stats[key]['control alert'] = 'Severe'
        else:
            if Subj_stats[key]['control value'] > 13.7:
                Subj_stats[key]['control alert'] = 'None'
            elif Subj_stats[key]['control value'] >= 11.1:
                Subj_stats[key]['control alert'] = 'Mild'
            elif Subj_stats[key]['control value'] >= 9.0:
                Subj_stats[key]['control alert'] = 'Moderate'
            else:
                Subj_stats[key]['control alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['control value'] > 12.7:
                Subj_stats[key]['control alert'] = 'None'
            elif Subj_stats[key]['control value'] >= 11.1:
                Subj_stats[key]['control alert'] = 'Mild'
            elif Subj_stats[key]['control value'] >= 9.0:
                Subj_stats[key]['control alert'] = 'Moderate'
            else:
                Subj_stats[key]['control alert'] = 'Severe'
        else:
            if Subj_stats[key]['control value'] > 12.9:
                Subj_stats[key]['control alert'] = 'None'
            elif Subj_stats[key]['control value'] >= 11.1:
                Subj_stats[key]['control alert'] = 'Mild'
            elif Subj_stats[key]['control value'] >= 9.0:
                Subj_stats[key]['control alert'] = 'Moderate'
            else:
                Subj_stats[key]['control alert'] = 'Severe'
                

for key in Subj_stats:
    if Subj_stats[key]['gender']=='f' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['last_hgb'] > 12.2:
            Subj_stats[key]['WHO actual alert'] = 'None'
        elif Subj_stats[key]['last_hgb'] >= 11.1:
            Subj_stats[key]['WHO actual alert'] = 'Mild'
        elif Subj_stats[key]['last_hgb'] >= 9.0:
            Subj_stats[key]['WHO actual alert'] = 'Moderate'
        else:
            Subj_stats[key]['WHO actual alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='f' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['last_hgb'] > 11.5:
            Subj_stats[key]['WHO actual alert'] = 'None'
        elif Subj_stats[key]['last_hgb'] >= 10.6:
            Subj_stats[key]['WHO actual alert'] = 'Mild'
        elif Subj_stats[key]['last_hgb'] >= 9.0:
            Subj_stats[key]['WHO actual alert'] = 'Moderate'
        else:
            Subj_stats[key]['WHO actual alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['last_hgb'] > 13.2:
                Subj_stats[key]['WHO actual alert'] = 'None'
            elif Subj_stats[key]['last_hgb'] >= 11.1:
                Subj_stats[key]['WHO actual alert'] = 'Mild'
            elif Subj_stats[key]['last_hgb'] >= 9.0:
                Subj_stats[key]['WHO actual alert'] = 'Moderate'
            else:
                Subj_stats[key]['WHO actual alert'] = 'Severe'
        else:
            if Subj_stats[key]['last_hgb'] > 13.7:
                Subj_stats[key]['WHO actual alert'] = 'None'
            elif Subj_stats[key]['last_hgb'] >= 11.1:
                Subj_stats[key]['WHO actual alert'] = 'Mild'
            elif Subj_stats[key]['last_hgb'] >= 9.0:
                Subj_stats[key]['WHO actual alert'] = 'Moderate'
            else:
                Subj_stats[key]['WHO actual alert'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['last_hgb'] > 12.7:
                Subj_stats[key]['WHO actual alert'] = 'None'
            elif Subj_stats[key]['last_hgb'] >= 11.1:
                Subj_stats[key]['WHO actual alert'] = 'Mild'
            elif Subj_stats[key]['last_hgb'] >= 9.0:
                Subj_stats[key]['WHO actual alert'] = 'Moderate'
            else:
                Subj_stats[key]['WHO actual alert'] = 'Severe'
        else:
            if Subj_stats[key]['last_hgb'] > 12.9:
                Subj_stats[key]['WHO actual alert'] = 'None'
            elif Subj_stats[key]['last_hgb'] >= 11.1:
                Subj_stats[key]['WHO actual alert'] = 'Mild'
            elif Subj_stats[key]['last_hgb'] >= 9.0:
                Subj_stats[key]['WHO actual alert'] = 'Moderate'
            else:
                Subj_stats[key]['WHO actual alert'] = 'Severe'
                
# check for anemia on admission
for key in Subj_stats:
    if Subj_stats[key]['gender']=='f' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['first_hgb'] > 12.2:
            Subj_stats[key]['Initial anemia'] = 'None'
        elif Subj_stats[key]['first_hgb'] >= 11.1:
            Subj_stats[key]['Initial anemia'] = 'Mild'
        elif Subj_stats[key]['first_hgb'] >= 9.0:
            Subj_stats[key]['Initial anemia'] = 'Moderate'
        else:
            Subj_stats[key]['Initial anemia'] = 'Severe'
    elif Subj_stats[key]['gender']=='f' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['first_hgb'] > 11.5:
            Subj_stats[key]['Initial anemia'] = 'None'
        elif Subj_stats[key]['first_hgb'] >= 10.6:
            Subj_stats[key]['Initial anemia'] = 'Mild'
        elif Subj_stats[key]['first_hgb'] >= 9.0:
            Subj_stats[key]['Initial anemia'] = 'Moderate'
        else:
            Subj_stats[key]['Initial anemia'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race'] not in ['black', 'other', 'unk', 'refused']:
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['first_hgb'] > 13.2:
                Subj_stats[key]['Initial anemia'] = 'None'
            elif Subj_stats[key]['first_hgb'] >= 11.1:
                Subj_stats[key]['Initial anemia'] = 'Mild'
            elif Subj_stats[key]['first_hgb'] >= 9.0:
                Subj_stats[key]['Initial anemia'] = 'Moderate'
            else:
                Subj_stats[key]['Initial anemia'] = 'Severe'
        else:
            if Subj_stats[key]['first_hgb'] > 13.7:
                Subj_stats[key]['Initial anemia'] = 'None'
            elif Subj_stats[key]['first_hgb'] >= 11.1:
                Subj_stats[key]['Initial anemia'] = 'Mild'
            elif Subj_stats[key]['first_hgb'] >= 9.0:
                Subj_stats[key]['Initial anemia'] = 'Moderate'
            else:
                Subj_stats[key]['Initial anemia'] = 'Severe'
    elif Subj_stats[key]['gender']=='m' and Subj_stats[key]['race']=='black':
        if Subj_stats[key]['age'] >= 60:
            if Subj_stats[key]['first_hgb'] > 12.7:
                Subj_stats[key]['Initial anemia'] = 'None'
            elif Subj_stats[key]['first_hgb'] >= 11.1:
                Subj_stats[key]['Initial anemia'] = 'Mild'
            elif Subj_stats[key]['first_hgb'] >= 9.0:
                Subj_stats[key]['Initial anemia'] = 'Moderate'
            else:
                Subj_stats[key]['Initial anemia'] = 'Severe'
        else:
            if Subj_stats[key]['first_hgb'] > 12.9:
                Subj_stats[key]['Initial anemia'] = 'None'
            elif Subj_stats[key]['first_hgb'] >= 11.1:
                Subj_stats[key]['Initial anemia'] = 'Mild'
            elif Subj_stats[key]['first_hgb'] >= 9.0:
                Subj_stats[key]['Initial anemia'] = 'Moderate'
            else:
                Subj_stats[key]['Initial anemia'] = 'Severe'
                
 # check the Lyons alert vs actual for TN, TP, FP, FN               
for key in Subj_stats:
    if Subj_stats[key]['WHO actual alert'] == 'None':
        if Subj_stats[key]['WHO actual alert'] == Subj_stats[key]['Lyons alert']:
            Subj_stats[key]['Lyons result'] = 'TN'
        elif Subj_stats[key]['WHO actual alert'] == 'None' and Subj_stats[key]['Lyons alert'] == 'Severe':
            Subj_stats[key]['Lyons result'] = 'FP'
    elif Subj_stats[key]['WHO actual alert'] == 'Severe':
        if Subj_stats[key]['WHO actual alert'] == Subj_stats[key]['Lyons alert']:
            Subj_stats[key]['Lyons result'] = 'TP'
        elif Subj_stats[key]['WHO actual alert'] == 'Severe' and Subj_stats[key]['Lyons alert'] == 'None':
            Subj_stats[key]['Lyons result'] = 'FN'
            
# check the control alert vs actual for TN, TP, FP, FN
for key in Subj_stats:
    if Subj_stats[key]['WHO actual alert'] == 'None':
        if Subj_stats[key]['WHO actual alert'] == Subj_stats[key]['control alert']:
            Subj_stats[key]['control result'] = 'TN'
        elif Subj_stats[key]['WHO actual alert'] == 'None' and Subj_stats[key]['control alert'] == 'Severe':
            Subj_stats[key]['control result'] = 'FP'
    elif Subj_stats[key]['WHO actual alert'] == 'Severe':
        if Subj_stats[key]['WHO actual alert'] == Subj_stats[key]['control alert']:
            Subj_stats[key]['control result'] = 'TP'
        elif Subj_stats[key]['WHO actual alert'] == 'Severe' and Subj_stats[key]['control alert'] == 'None':
            Subj_stats[key]['control result'] = 'FN'
            
# use a grouping of None/Mild and Moderate/Severe
for key in Subj_stats:
    if Subj_stats[key]['WHO actual alert'] in ['None', 'Mild']:
        if Subj_stats[key]['Lyons alert'] in ['None', 'Mild']:
            Subj_stats[key]['Lyons grouping'] = 'TN'
        elif Subj_stats[key]['Lyons alert'] in ['Moderate', 'Severe']:
            Subj_stats[key]['Lyons grouping'] = 'FP'
    elif Subj_stats[key]['WHO actual alert'] in ['Moderate', 'Severe']:
        if Subj_stats[key]['Lyons alert'] in ['Moderate', 'Severe']:
            Subj_stats[key]['Lyons grouping'] = 'TP'
        elif Subj_stats[key]['Lyons alert'] in ['None', 'Mild']:
            Subj_stats[key]['Lyons grouping'] = 'FN'
            
# continue use of grouping for control algorithm          
for key in Subj_stats:
    if Subj_stats[key]['WHO actual alert'] in ['None', 'Mild']:
        if Subj_stats[key]['control alert'] in ['None', 'Mild']:
            Subj_stats[key]['control grouping'] = 'TN'
        elif Subj_stats[key]['control alert'] in ['Moderate', 'Severe']:
            Subj_stats[key]['control grouping'] = 'FP'
    elif Subj_stats[key]['WHO actual alert'] in ['Moderate', 'Severe']:
        if Subj_stats[key]['control alert'] in ['Moderate', 'Severe']:
            Subj_stats[key]['control grouping'] = 'TP'
        elif Subj_stats[key]['control alert'] in ['None', 'Mild']:
            Subj_stats[key]['control grouping'] = 'FN'
            
            
            
Subj_data = pd.DataFrame.from_dict(Subj_stats, orient='index')
Subj_data['Hgb diff'] = Subj_data['first_hgb'] - Subj_data['last_hgb']
Subj_data = Subj_data[Subj_data['control alert'] != 'N/A']
Subj_data.set_index('mrn')

# create separate data set that omits MRN to make it easier for plotting
Data_no_mrn = Subj_data.reset_index(drop=True)
Data_no_mrn.drop(labels=['mrn'], axis=1, inplace=True)

# create subset of data for AA population
aa_data = Data_no_mrn[Data_no_mrn['race'] == 'black']

#data analysis plots

# histogram of age distribution
plt.hist(Subj_data['age'], bins=15, range=(20, 100), color='blue')
plt.xlabel('Age')
plt.ylabel('# Subjects')
plt.title('Study Population Age Distribution')
plt.savefig('Age distribution2.png')

# scatter plot of length of stay vs. hgb difference
plt.scatter(Subj_data['days'], Subj_data['Hgb diff'])
plt.show()

# scatter plot of draw volume vs. hgb difference
plt.scatter(Subj_data['draw_volume'], Subj_data['Hgb diff'])
plt.show()

# exploratory plots
from pandas.plotting import scatter_matrix
scatter_matrix(Data_no_mrn, figsize=(30, 30))
plt.savefig('Subj_data scatter matrix2.png')

# correlation matrix

sns.set(style="white")
corr = Data_no_mrn
corr = corr.corr()
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
 # tweak the size of the plot to make numbers easier to read
f, ax = plt.subplots(figsize=(15,15))


# produce heatmap using 3 decimal places for Pearson correlation values
sns.heatmap(corr, mask=mask, cmap='seismic', robust=True, annot=True, annot_kws={'size':14}, fmt='.3f', square=True)
ax.set_title('Correlation of Numeric Data Set Variables', fontdict={'fontsize': 24})
plt.yticks(fontsize=12, rotation=0)
plt.xticks(fontsize=12, rotation=90)
#plt.show()
plt.savefig('Correlation plot2.png')

# reproduce correlation plot for AA population
sns.set(style="white")
corr2 = aa_data
corr2 = corr2.corr()
mask2 = np.zeros_like(corr2, dtype=np.bool)
mask2[np.triu_indices_from(mask2)] = True
 # tweak the size of the plot to make numbers easier to read
f, ax = plt.subplots(figsize=(15,15))


# produce heatmap using 3 decimal places for Pearson correlation values
sns.heatmap(corr2, mask=mask2, cmap='seismic', robust=True, annot=True, annot_kws={'size':14}, fmt='.3f', square=True)
ax.set_title('Correlation of Numeric Data Set Variables', fontdict={'fontsize': 24})
plt.yticks(fontsize=12, rotation=0)
plt.xticks(fontsize=12, rotation=90)
#plt.show()
plt.savefig('AA Correlation plot.png')


