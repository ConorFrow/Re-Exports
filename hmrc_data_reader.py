from pandas import DataFrame, to_numeric
import os

month, comcode, sitc, c_dis, port, c_orig, val, n_c_dis, n_port, n_c_orig, hs_two, sitc_dict, transport, sitc_i, sitc_ii, sitc_iii, sitc_iv, sitc_v, area_dis, area_orig, cntry_dict, dist_dict = [], [], [], [], [], [], [], [], [], [], [], {}, [], [], [], [], [], [], [], [], {}, {}
sitc_all = [sitc_i, sitc_ii, sitc_iii, sitc_iv, sitc_v]
##List of EU countries
eu = ('AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'EL', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE')


#These three functions are used to map Names/Values to their respective country codes in the dataset
def eu_non(country):
    if country in eu:
        return 'EU'
    elif country == '  ':
        return 'N/A'
    else:
        return 'Non-EU'



#Splits the Latitude and Longitude section of the All Country Data string and converts to float so we can calculate distance
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




for file in os.listdir():
##Reading relevant text files and splitting all lines by '\n' so they can be read individually
    if file.endswith('.txt') and file != 'SITC codes.txt' and file != 'All Country Data.txt' and file != 'Continents temp.txt':
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

temp = ['SITC codes', 'All Country Data']

for i in range(2):
    file_ = open(fr'../Rotterdam Effect/{temp[i]}.txt', 'r', encoding = 'utf8')
    text = file_.read()
    file_.close() 
    temp.append(text.split('\n'))

sitc_names, cntry_all = temp[-2], temp[-1]    

#Creating a dictionary that maps SITC code and country code to its title - need to try and loop this part nicely (if useful)


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


#Mapping lists to datset (could maybe use single function to map all three groups?) (going to try make SITC and country list tuples)
area_dis, area_orig = list(map(eu_non, c_dis)), list(map(eu_non, c_orig))                   #EU or non-EU
c_dis_coord, c_orig_coord = list(map(coord, c_dis)), list(map(coord, c_orig))               #Longitude and latitude
c_dis_name, c_orig_name = list(map(country_name, c_dis)), list(map(country_name, c_orig))   #Country Names
sitc_i, sitc_ii = list(map(sitc_code, sitc_i)), list(map(sitc_code, sitc_ii))               #SITC Codes


##Creating the main dataframe
data = {'Year-Month' : month, 'Commodity Code' : comcode, 'SITC level 1' : sitc_i, 'SITC level 2' : sitc_ii, 'Country of Dispatch' : c_dis_name, 'Country of Dispatch Code' : c_dis, 'Country of Dispatch Co-ords' : c_dis_coord, 'Port of Dispatch' : port, 'Area of Dispatch' : area_dis, 'Country of Origin' : c_orig_name, 'Country of Origin Code' : c_orig, 'Country of Origin Co-ords' : c_orig_coord, 'Area of Origin' : area_orig, 'Value' : val, 'Method of Transport' : transport}
df = DataFrame(data = data)
del month, comcode, sitc_i, sitc_ii, c_dis, port, c_orig, val, n_c_dis, n_port, n_c_orig, transport
df['Value'] = to_numeric(df['Value'])
df['Value'] = df['Value']/1000000
df.to_pickle(r'../Rotterdam Effect/nov_data.pkl')