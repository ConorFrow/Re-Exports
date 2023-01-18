start = 0
#Helping with run times by running part of the code that is needed
while start == 0:
    what_to_run = input('Tables = 1 | QA = 2 | Both = 3: ---> ')
    if what_to_run == '1' or what_to_run == '2' or what_to_run == '3':
        start += 1
    else:
        print('Try again...')
'-------------------------------------------------------------------------------------------'
##Importing modules that may/may not be needed
import pandas as pd
import os
from math import radians, cos, sin, asin, sqrt


###Fun Fun Functions
#Calculates distance between two locations using latitude and longitude, used for QA
def dist_calc(country_1_coords, country_2_coords):
    #converts from degrees to radians
    long1, long2 = country_1_coords[1], country_2_coords[1]
    lat1, lat2 = country_1_coords[0], country_2_coords[0]
    long1, long2, lat1, lat2 = radians(long1), radians(long2), radians(lat1), radians(lat2)     
    # Haversine formula
    dlong, dlat = long2 - long1, lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlong / 2)**2
    c, r = 2 * asin(sqrt(a)), 6371
    return(c * r)



#Temporary (I can find a better way), distance between UK and selected country
def dist_calcuk(country_2_coords):
    #converts from degrees to radians
    long1, long2 = -3.435973, country_2_coords[1]
    lat1, lat2 = 55.378051, country_2_coords[0]
    long1, long2, lat1, lat2 = radians(long1), radians(long2), radians(lat1), radians(lat2)     
    # Haversine formula
    dlong, dlat = long2 - long1, lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlong / 2)**2
    c, r = 2 * asin(sqrt(a)), 6371
    return(c * r)



#These three functions are used to map Names/Values to their respective country codes in the dataset
def eu_non(country):
    if country in eu:
        return 'EU'
    elif country == '  ':
        return 'N/A'
    else:
        return 'Non-EU'

#Splits the Latitude and Longitude section of the string and converts to float so we can calculate distance
def coord(country):
    temp = dist_dict[country].split(' ')
    return [float(temp[0]), float(temp[1])]



def country_name(country):
    return cntry_dict[country]



#Using the dictionary to update the SITC codes in the dataset - issues caused by suppressed and unknown data are corrected in 2 ways (as they dont appear in the list of commodities used to make dictionary): 
#All unknown data ends with '-', so use that to identify them, all suppressed data is covered by the 'try' loop, which runs different code to correct the issue if a KeyError appears 
def sitc_code(sitc_level):
    try:    
        if '-' not in sitc_level:
            return sitc_dict[sitc_level]
        else: 
            return f"{sitc_level[:sitc_level.find('-'):]} Non Response Estimates"
    except KeyError:
        return f"{sitc_level[:-1:]} - Suppressed for Confidentiality"
    
'-------------------------------------------------------------------------------------------'
###ORGANISING DATA


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
            if i.find('QV') == -1 and i.find('YY') == -1 and i.find('ZY') == -1 and i[40:42:] != '  ':
                month.append(i[:6:]), comcode.append(i[13:21:]), sitc_i.append(i[21:22:]), sitc_ii.append(i[21:23:]), c_dis.append(i[29:31:]), port.append(i[34:37:]), c_orig.append(i[40:42:]), val.append(float(i[44:56:])), n_c_dis.append(i[26:29:]), n_port.append(i[31:34:]), n_c_orig.append(i[37:40:]), transport.append(i[42:44:])

##Reading/Using File to link SITC code with commodity names (file wont read unless encoding = utf8 is used ???)

temp = ['SITC codes', 'Country Distances/All Country Data']

for i in range(2):
    file_ = open(fr'../Rotterdam Effect/{temp[i]}.txt', 'r', encoding = 'utf8')
    text = file_.read()
    file_.close() 
    temp.append(text.split('\n'))

sitc_names, cntry_all = temp[-2], temp[-1]    

#Creating a dictionary that maps SITC code and country code to its title - need to try and loop this part nicely (if useful)
print('Making Dicts')
for i in sitc_names:
    sitc_dict[i[:i.find('\t'):]] = i[i.find('\t')+1::]

hold = []
long, lat = [], []
for i in cntry_all:
    hold.append(i.split('\t'))

for i in hold:
    cntry_dict[i[0]] = i[3]
    long.append(i[1]), lat.append(i[2])
    dist_dict[i[0]] = i[1] + ' ' + i[2]       




print('Mapping')
#Mapping lists to datset (could maybe use single function to map all three groups?) (going to try make SITC and country list tuples)
area_dis, area_orig = list(map(eu_non, c_dis)), list(map(eu_non, c_orig))                   #EU or non-EU
c_dis_coord, c_orig_coord = list(map(coord, c_dis)), list(map(coord, c_orig))               #Longitude and latitude
c_dis_name, c_orig_name = list(map(country_name, c_dis)), list(map(country_name, c_orig))   #Country Names
sitc_i, sitc_ii = list(map(sitc_code, sitc_i)), list(map(sitc_code, sitc_ii))               #SITC Codes

print('Creating main dataframe')
##Creating the main dataframe
data = {'Year-Month' : month, 'Commodity Code' : comcode, 'SITC level 1' : sitc_i, 'SITC level 2' : sitc_ii, 'Country of Dispatch' : c_dis_name, 'Country of Dispatch Code' : c_dis, 'Country of Dispatch Co-ords' : c_dis_coord, 'Port of Dispatch' : port, 'Area of Dispatch' : area_dis, 'Country of Origin' : c_orig_name, 'Country of Origin Code' : c_orig, 'Country of Origin Co-ords' : c_orig_coord, 'Area of Origin' : area_orig, 'Value' : val, 'Method of Transport' : transport}
df = pd.DataFrame(data = data)
df['Value'] = pd.to_numeric(df['Value'])
df['Value'] = df['Value']/1000000


'-------------------------------------------------------------------------------------------'
###ANALYSIS STUFF
if what_to_run == '1' or what_to_run == '3':
    print('Making Everything Else')
    
    #All data where disp != orig    
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
    df_transp.columns = ['Total count', 'Count when Disp != Orig']
    df_transp['Total count %'], df_transp['Disparity count %'] = df_transp['Total count']*100/df_transp['Total count'].sum(), df_transp['Count when Disp != Orig']*100/df_transp['Count when Disp != Orig'].sum()
    df_transp.to_excel(wr, sheet_name = 'Transport')
    
    
    #Table showing what commodities are primarily re-exported by each country 
    for v in class_:  
        df_cmdty = df_disparity.groupby(['SITC level 1', 'SITC level 2', f'Country of {v}'])['Value'].sum()
        df_cmdty = df_cmdty.rename_axis(['SITC Level 1', 'SITC level 2', f'Country of {v}']).reset_index()   
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
if what_to_run == '1' or what_to_run == '3':
    ###QA
    print('QA')
    check = ['NL', 'DE', 'BE', 'FR', 'CH', 'IT', 'ES']
    check1, check2, checked_all = [], [], []
    for i in check:
        check1.append(list(i[0]))
        check2.append(list(i[1]))
    checks = [check1, check2]
    
    df_qa = df_disparity[df_disparity['Country of Origin'] != 'United Kingdom'].copy().reset_index()
    
    df_qa['Dist Travelled'] = list(map(dist_calc, df_qa['Country of Origin Co-ords'], df_qa['Country of Dispatch Co-ords']))
    
    df_qa['uk_orig'] = list(map(dist_calcuk, df_qa['Country of Origin Co-ords'])) 
    df_qa['uk_disp'] = list(map(dist_calcuk, df_qa['Country of Dispatch Co-ords']))
    df_qa['Dist diff'] = df_qa['uk_orig'] - df_qa['uk_disp']
    df_qa['Ratio'] = df_qa['Dist diff']/df_qa['Dist Travelled']
    
    df_qa = df_qa[df_qa['Dist diff'] < -1000]        
    df_qa = df_qa.groupby(['Country of Origin', 'Country of Dispatch', 'Country of Origin Code', 'Country of Dispatch Code', 'Dist Travelled', 'Dist diff', 'Ratio'])['Value'].agg(['sum', 'count']).reset_index()
    
    for i in df_qa['Country of Dispatch Code']:
        checked = []
        for z in range(2):
            if list(i[z]) in checks[z]:
                checked.append(check[checks[z].index(list(i[z]))])
        if checked == []:
            checked.append('-')
        checked_all.append(', '.join(checked))
        
    df_qa['Dispatch Check'] = checked_all
    
    df_qa_overview = df_qa[(df_qa['count'] < 12) & (df_qa['Dispatch Check'] != '-')].groupby(['Country of Dispatch Code', 'Dispatch Check'])[['sum', 'count']].sum().reset_index()
    df_qa_overview_2 = df_qa[df_qa['count'] < 12].groupby(['Dispatch Check'])[['sum', 'count']].sum().reset_index()

'-------------------------------------------------------------------------------------------'

##IMPORTANT
#NA values for country of origin are classified as Non-EU

###NOTES
#Country Codes [CTRL + Click]:https://www.gov.uk/government/publications/uk-trade-tariff-country-and-currency-codes/uk-trade-tariff-country-and-currency-codes
#Website that links HS codes to names (at different levels): https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_CLS_DLD&StrNom=HS_2002&StrLanguageCode=EN#
#All different commodity classification types: https://unstats.un.org/unsd/classifications/Econ