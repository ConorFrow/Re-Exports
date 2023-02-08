### This Branch allows you to run the hmrc_data_reader code once to save a pickle with the dataframe in the file, then run the main file to do analysis
### Just did this to save myself/others loading in all the data every time, instruction below arent updated yet
### BEFORE RUNNING:
# Place the code and the two text files ['(Working) Trade Origin Project.py', 'All Country Data.txt', 'SITC codes'] in a single folder, doesn't matter what
# the name is.
# In the same folder place all the HMRC data text files you want to read ['BDSimpYYMM.txt']. 

### RUNNING THE CODE:
# After running the code you will be prompted to choose what output you want in the Console, type 1/2/3 + ENTER to choose.

### OUTPUT:
# All tables produced will be found in an excel file named 'Pre-made Analysis re-exports.xlsx', which will appear in the same folder as everything else.
# The QA dataframes can be found in the variable explorer as: ['df_qa', 'df_qa_overview', df_qa_overview_2']
