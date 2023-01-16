##Hello and welcome to my code, I hope you enjoy your stay

###INSTRUCTIONS FOR RUNNING
#Ensure this code is saved in the same file as any text files you want to read
#Name the folder: Rotterdam Effect (or change the name in: '../folder_name/{file}' on highlighted lines to your own folder name)


'-------------------------------------------------------------------------------------------'
###ORGANISING DATA
##Importing modules that may/may not be needed
import pandas as pd
import os

##Creating lists to add to when reading text files
month, comcode, sitc, c_dis, port, c_orig, val, n_c_dis, n_port, n_c_orig, hs_two, sitc_dict, transport, sitc_i, sitc_ii, sitc_iii, sitc_iv, sitc_v, area_dis, area_orig, cntry_dict, dist_dict = [], [], [], [], [], [], [], [], [], [], [], {}, [], [], [], [], [], [], [], [], {}, {}
sitc_all = [sitc_i, sitc_ii, sitc_iii, sitc_iv, sitc_v]
##List of EU countries
eu = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'EL', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']

#Setting up exporting to Excel
wr = pd.ExcelWriter('Pre-made Analysis re-exports.xlsx')

print('Reading Files')
##Getting all files from current directory(folder) ending in .txt
for file in os.listdir():
##Reading relevant text files and splitting all lines by '\n' so they can be read individually
    if file.endswith('.txt') and file != 'SITC codes.txt' and file != 'Country Codes.txt':
        print(file)
        file_ = open(fr'../Rotterdam Effect/{file}', 'r')
        text = file_.read()
        file_.close() 
        all_d = text.split('\n')
        #deleting the title and empty space at end
        del all_d[0], all_d[-1]   

##Slicing the important information out of each line and placing it in a list
##If format changes/adding new items to table: variable_name.append(i[Start number - 1:End number:])

        for i in all_d:
            if i.find('QV') == -1 and i.find('YY') == -1 and i.find('ZY') == -1 and i[44:56:] != '':
                month.append(i[:6:]), comcode.append(i[13:21:]), sitc_i.append(i[21:22:]), sitc_ii.append(i[21:23:]), sitc_iii.append(i[21:24:]), sitc_iv.append(i[21:25:]), sitc_v.append(i[21:26:]), c_dis.append(i[29:31:]), port.append(i[34:37:]), c_orig.append(i[40:42:]), val.append(i[44:56:]), n_c_dis.append(i[26:29:]), n_port.append(i[31:34:]), n_c_orig.append(i[37:40:]), transport.append(i[42:44:])

##Reading/Using File to link SITC code with commodity names (file wont read unless encoding = utf8 is used ???)



temp = ['SITC codes', 'Country Codes', 'Country Distances/Distance']

for i in range(3):
    file_ = open(fr'../Rotterdam Effect/{temp[i]}.txt', 'r', encoding = 'utf8')
    text = file_.read()
    file_.close() 
    temp.append(text.split('\n'))

sitc_names, cntry_names, dist_all = temp[-3], temp[-2], temp[-1]    

#Creating a dictionary that maps SITC code and country code to its title - need to try and loop this part nicely (if useful)
print('Loop 1')
for i in sitc_names:
    sitc_dict[i[:i.find('\t'):]] = i[i.find('\t')+1::]

for i in cntry_names:
    if i.find('(') == -1:
        cntry_dict[i[:i.find('\t'):]] = i[i.find('\t')+1::]
    else:
        cntry_dict[i[:i.find('\t'):]] = i[i.find('\t')+1:i.find('(')-1:]
        
for i in dist_all:
    dist_dict[i[:i.find('\t'):]] = i[i.find('\t')+1::]

#Using the dictionary to update the SITC codes in the dataset - issues caused by suppressed and unknown data are corrected in 2 ways (as they dont appear in the list of commodities used to make dictionary): 
#All unknown data ends with '-', so use that to identify them, all suppressed data is covered by the 'try' loop, which runs different code to correct the issue if a KeyError appears 
print('Naming SITC codes and Country Codes')
for v in sitc_all:
#in this loop, list(enumerate(variable)) creates a list of all the items in v, assigning an index value to each one (Looks something like [(0,'first item'), (1,'second item')]) etc. i and t then take these values in each loop
    for i, t in list(enumerate(v)):
        try:    
            if '-' not in t:
                v[i] = sitc_dict[t]
            else: 
                v[i] = f"{t[:t.find('-'):]} Non Response Estimates"
        except KeyError:
            v[i] = f"{t[:-1:]} - Suppressed for Confidentiality"


print('Creating main dataframe')
data = {'Year-Month' : month, 'Commodity Code' : comcode, 'SITC level 1' : sitc_i, 'SITC level 2' : sitc_ii, 'SITC level 3' : sitc_iii, 'SITC Level 5' : sitc_v, 'Country of Dispatch' : c_dis, 'Country of Dispatch Code' : c_dis, 'Port of Dispatch' : port, 'Country of Origin' : c_orig, 'Country of Origin Code' : c_orig, 'Value' : val, 'Method of Transport' : transport}

##Creating the main dataframe
df = pd.DataFrame(data = data)
df['Value'] = pd.to_numeric(df['Value'])
df['Value'] = df['Value']/1000000

for i in ['Dispatch', 'Origin']:       
    df[f'Area of {i}'] = ['EU' if i in eu else 'Non-EU' for i in df[f'Country of {i}']]
    df.replace({f'Country of {i}' : cntry_dict}, inplace = True)
    df[f'{i} Distance'] = df[f'Country of {i}']
    df.replace({f'{i} Distance' : dist_dict}, inplace = True)



'-------------------------------------------------------------------------------------------'
###ANALYSIS STUFF

print('Making Everything Else')
#Simple table, just shows all data where disp != orig    
df_disparity = df[df['Country of Dispatch'] != df['Country of Origin']]


#Time series
dates, class_ = (df_disparity['Year-Month'].unique()).tolist(), ['Origin', 'Dispatch']
for v in class_:    
    df_ts = ((df_disparity[df_disparity['Year-Month'] == f'{dates[0]}']).groupby([f'Country of {v}', 'SITC level 1'])['Value'].sum()).rename(f'{dates[0]}')
    for i in dates[1::]:
        df_temp = (df_disparity[df_disparity['Year-Month'] == f'{i}']).groupby([f'Country of {v}', 'SITC level 1'])['Value'].sum()
        df_ts = pd.concat([df_ts, df_temp], axis = 1, join = 'outer').rename(columns = {'Value' : f'{i}'})
    df_ts = df_ts.rename_axis([v, 'SITC level 1']).reset_index()    
    df_ts.to_excel(wr, sheet_name = f'Time Series by {v}', index = False)

#EU/non-EU time series (it will be possible to loop the above and below, I will do that later (maybe))
df_disparity = df[df['Area of Dispatch'] != df['Area of Origin']]

for v in class_:    
    df_ts = ((df_disparity[df_disparity['Year-Month'] == f'{dates[0]}']).groupby([f'Area of {v}', 'SITC level 1'])['Value'].sum()).rename(f'{dates[0]}')
    for i in dates[1::]:
        df_temp = (df_disparity[df_disparity['Year-Month'] == f'{i}']).groupby([f'Area of {v}', 'SITC level 1'])['Value'].sum()
        df_ts = pd.concat([df_ts, df_temp], axis = 1, join = 'outer').rename(columns = {'Value' : f'{i}'})
    df_ts = df_ts.rename_axis([v, 'SITC level 1']).reset_index()    
    df_ts.to_excel(wr, sheet_name = f'EU Time Series by {v}', index = False)


#Table that compares each countries import value when using dispatch vs origin
dfl = [df.groupby('Country of Dispatch')['Value'].sum(), df.groupby('Country of Origin')['Value'].sum(), df_disparity.groupby('Country of Dispatch')['Value'].sum()]
df_diff = pd.concat(dfl, axis = 1) 
df_diff.columns = ['Dispatch', 'Origin', 'Re-Export Value']
df_diff['Disp - Orig'] = df_diff.iloc[:, 0] - df_diff.iloc[:, 1]
df_diff = df_diff.sort_values(by = ['Disp - Orig'], ascending = False)
df_diff.to_excel(wr, sheet_name = 'Re-Export value by Country')


#Table showing what methods of Transport are seen when there is a disparity (as a % of total) vs total %
dfl = [df.groupby('Method of Transport').size(), df_disparity.groupby('Method of Transport').size()]
df_transp = pd.concat(dfl, axis = 1)
df_transp, df_transp.columns = df_transp.drop('  '), ['Total count', 'Count when Disp != Orig']
df_transp['Total count %'], df_transp['Disparity count %'] = df_transp['Total count']*100/df_transp['Total count'].sum(), df_transp['Count when Disp != Orig']*100/df_transp['Count when Disp != Orig'].sum()
df_transp.to_excel(wr, sheet_name = 'Transport')


#Table showing what commodities are primarily re-exported by each country 
for v in class_:  
    df_cmdty = df_disparity.groupby(['SITC level 1', 'SITC level 3', f'Country of {v}'])['Value'].sum()
    df_cmdty = df_cmdty.rename_axis(['SITC Level 1', 'SITC level 3', f'Country of {v}']).reset_index()   
    df_cmdty.to_excel(wr, sheet_name = f'Re-Exp Cmdty by {v}', index = False)


wr.save()

###Ukraine temp
ua = df_disparity[df_disparity['Country of Origin'] == 'Ukraine']


df_ts = ((ua[ua['Year-Month'] == f'{dates[0]}']).groupby(['Country of Dispatch', 'SITC level 1'])['Value'].sum()).rename(f'{dates[0]}')
for i in dates[1::]:
    df_temp = (ua[ua['Year-Month'] == f'{i}']).groupby(['Country of Dispatch', 'SITC level 1'])['Value'].sum()
    df_ts = pd.concat([df_ts, df_temp], axis = 1, join = 'outer').rename(columns = {'Value' : f'{i}'})
df_ts = df_ts.rename_axis(['Country of Dispatch', 'SITC level 1']).reset_index()    


abc = df_disparity.copy()
abc = abc[abc['Country of Dispatch'] == 'Netherlands']
abc = abc.groupby(['Country of Origin', 'SITC level 1', 'SITC level 2'])['Value'].sum()
abc = abc.rename_axis(['Origin', 'SITC Level 1', 'SITC level 2']).reset_index()


'-------------------------------------------------------------------------------------------'
###QA
check = ['NL', 'DE', 'BE', 'FR', 'CH', 'IT', 'ES']
check1, check2, checked_all = [], [], []
for i in check:
    check1.append(list(i[0]))
    check2.append(list(i[1]))
checks = [check1, check2]


print('QA')
df_dist = df[(df['Origin Distance'] != '  ') & (df['Country of Origin'] != 'United Kingdom')].copy()
df_dist[['Origin Distance', 'Dispatch Distance']] = df_dist[['Origin Distance', 'Dispatch Distance']].astype(int)
df_dist['Dist diff'] = df_dist['Origin Distance'] - df_dist['Dispatch Distance']
df_dist = df_dist[((abs(df_dist['Dist diff'])/df_dist['Origin Distance']) < 0.1)] 
                  #& (df_dist['Dist diff'] < -1000)]        
df_dist = df_dist.groupby(['Country of Origin', 'Country of Dispatch', 'Country of Origin Code', 'Country of Dispatch Code', 'Dist diff'])['Value'].agg(['sum', 'count']).reset_index()

for i in df_dist['Country of Dispatch Code']:
    checked = []
    for z in range(2):
        if list(i[z]) in checks[z]:
            checked.append(check[checks[z].index(list(i[z]))])
    if checked == []:
        checked.append('-')
    checked_all.append(', '.join(checked))
    
df_dist['Origin Check'] = checked_all
'-------------------------------------------------------------------------------------------'

##IMPORTANT
#NA values for country of origin are classified as Non-EU

###NOTES
#Country Codes [CTRL + Click]:https://www.gov.uk/government/publications/uk-trade-tariff-country-and-currency-codes/uk-trade-tariff-country-and-currency-codes
#Website that links HS codes to names (at different levels): https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_CLS_DLD&StrNom=HS_2002&StrLanguageCode=EN#
#All different commodity classification types: https://unstats.un.org/unsd/classifications/Econ