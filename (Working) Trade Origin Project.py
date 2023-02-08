start = 0
#Helping with run times by running part of the code that is needed
while start == 0:
    what_to_run = input('Tables = 1 | QA = 2 | Both = 3: ---> ')
    if what_to_run == '1' or what_to_run == '2' or what_to_run == '3':
        start += 1
    else:
        print('Try again...')
'-------------------------------------------------------------------------------------------'
##Importing modules
from pandas import ExcelWriter, concat, read_pickle
from math import radians, cos, sin, asin, sqrt
import time

timer = float(time.time())

###Fun Fun Functions
#Calculates distance between two locations using latitude and longitude, used for QA
def dist_calc(country_1_coords, country_2_coords):
    #converting from degrees to radians
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


#Timer to check what parts of the code are slowing things down
def timer_f(timers):
    return timers - float(time.time())   
    timers = float(time.time())
'-------------------------------------------------------------------------------------------'
###ORGANISING DATA


#Setting up exporting to Excel
wr = ExcelWriter('Pre-made Analysis re-exports.xlsx')


print('Start', f'{timer_f(timer)}')

df = read_pickle('C:/Users/frowc/OneDrive - Office for National Statistics/Rotterdam Effect/Files we dont want to run (ignore)/nov_data.pkl')

#All data where disp != orig    
df_disparity = df[df['Country of Dispatch'] != df['Country of Origin']]
'-------------------------------------------------------------------------------------------'
###ANALYSIS STUFF
if what_to_run == '1' or what_to_run == '3':

    print('Made main dataframe', round(float(f'{timer_f(timer)}'), 2))
        
    #Time series
    dates, class_ = (df_disparity['Year-Month'].unique()).tolist(), ['Origin', 'Dispatch']
    for v in class_:    
        df_ts = ((df_disparity[df_disparity['Year-Month'] == f'{dates[0]}']).groupby([f'Country of {v}', 'SITC level 1'])['Value'].sum()).rename(f'{dates[0]}')
        for i in dates[1::]:
            df_temp = (df_disparity[df_disparity['Year-Month'] == f'{i}']).groupby([f'Country of {v}', 'SITC level 1'])['Value'].sum()
            df_ts = concat([df_ts, df_temp], axis = 1, join = 'outer').rename(columns = {'Value' : f'{i}'})
        df_ts = df_ts.rename_axis([v, 'SITC level 1']).reset_index()    
        df_ts.to_excel(wr, sheet_name = f'Time Series by {v}', index = False)
    
    #EU/non-EU time series (it will be possible to loop the above and below, I will do that later (maybe))
    df_disparity = df[df['Area of Dispatch'] != df['Area of Origin']]
    
    for v in class_:    
        df_ts = ((df_disparity[df_disparity['Year-Month'] == f'{dates[0]}']).groupby([f'Area of {v}', 'SITC level 1'])['Value'].sum()).rename(f'{dates[0]}')
        for i in dates[1::]:
            df_temp = (df_disparity[df_disparity['Year-Month'] == f'{i}']).groupby([f'Area of {v}', 'SITC level 1'])['Value'].sum()
            df_ts = concat([df_ts, df_temp], axis = 1, join = 'outer').rename(columns = {'Value' : f'{i}'})
        df_ts = df_ts.rename_axis([v, 'SITC level 1']).reset_index()    
        df_ts.to_excel(wr, sheet_name = f'EU Time Series by {v}', index = False)
    
    
    #Table that compares each countries import value when using dispatch vs origin
    dfl = [df.groupby('Country of Dispatch')['Value'].sum(), df.groupby('Country of Origin')['Value'].sum(), df_disparity.groupby('Country of Dispatch')['Value'].sum()]
    df_diff = concat(dfl, axis = 1) 
    df_diff.columns = ['Dispatch', 'Origin', 'Re-Export Value']
    df_diff['Disp - Orig'] = df_diff.iloc[:, 0] - df_diff.iloc[:, 1]
    df_diff = df_diff.sort_values(by = ['Disp - Orig'], ascending = False)
    df_diff.to_excel(wr, sheet_name = 'Re-Export value by Country')
    
    
    #Table showing what methods of Transport are seen when there is a disparity (as a % of total) vs total %
    dfl = [df.groupby('Method of Transport').size(), df_disparity.groupby('Method of Transport').size()]
    df_transp = concat(dfl, axis = 1)
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
        df_ts = concat([df_ts, df_temp], axis = 1, join = 'outer').rename(columns = {'Value' : f'{i}'})
    df_ts = df_ts.rename_axis(['Country of Dispatch', 'SITC level 1']).reset_index()    
    
    
    abc = df_disparity.copy()
    abc = abc[abc['Country of Dispatch'] == 'Netherlands']
    abc = abc.groupby(['Country of Origin', 'SITC level 1', 'SITC level 2'])['Value'].sum()
    abc = abc.rename_axis(['Origin', 'SITC Level 1', 'SITC level 2']).reset_index()


'-------------------------------------------------------------------------------------------'
if what_to_run == '2' or what_to_run == '3':
    ###QA

    print('Made Everything else', round(float(f'{timer_f(timer)}'), 2))
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


    print("QA'd", round(float(f'{timer_f(timer)}'), 2))
'-------------------------------------------------------------------------------------------'

##IMPORTANT
#NA values for country of origin are classified as Non-EU

###NOTES
#Country Codes [CTRL + Click]:https://www.gov.uk/government/publications/uk-trade-tariff-country-and-currency-codes/uk-trade-tariff-country-and-currency-codes
#Website that links HS codes to names (at different levels): https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_CLS_DLD&StrNom=HS_2002&StrLanguageCode=EN#
#All different commodity classification types: https://unstats.un.org/unsd/classifications/Econ