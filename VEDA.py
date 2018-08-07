#import functions

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ConfigParser

Config = ConfigParser.ConfigParser() #initialize the config parser

Param_dict = {'Air_Temperature': 't', 'Humidity': 'rh', 'Soil_Humidity_100': 'SH_100'} #Setup a dictionary for mapping the variable names
Param_dict_rev = dict(map(reversed,Param_dict.items()))

def read_data(path = 'C:/Users/darrie/Desktop/Data_MET/Input/VST_Setur_MET.dat'):
    df = pd.read_csv(path, header = [1], skiprows = [2,3], index_col = 0)
    df = df.drop(['TOA5', 'TIMESTAMP', 'TS', np.nan])
    df = df[df.columns.values].astype(float)
    return(df)

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("Skip: %s" % option)
        except:
            print("exception on %s!" %option)
            dict[option] = SectionOne
    return(dict1)

def read_config(Param = 'Air_Temperature'):
    Config.read("c:\Users\darrie\Desktop\Config_Files\GlobalConfigQC1.ini") #Read the Config ini file
    Config_dict = ConfigSectionMap(Param)
    return (Config_dict)

def QC1_Flag(df, Param, Config_dict):

    QC_series = pd.Series(0, index = df.index)
    df['Delta'] = abs(df[Param_dict[Param]].diff()).gt(float(Config_dict['maxdelta']))
    df['Max'] = df[Param_dict[Param]].gt(float(Config_dict['max']))
    df['Min'] = df[Param_dict[Param]].lt(float(Config_dict['min']))
    df['Missing'] = df[Param_dict[Param]].isnull()

    for index, row in df.iterrows():
        if row['Delta'] == True:
            QC_series[index] = 'Step too large'
        elif row['Max'] == True:
            QC_series[index] = 'Out of bounds'
        elif row['Min'] == True:
            QC_series[index] = 'Out of bounds'
        elif row['Missing'] == True:
            QC_series[index] = 'Missing value'
        else:
            QC_series[index] = 'Good'

    df[Param_dict[Param] + '_QC1'] = QC_series
    df = df.drop(labels = ['Delta', 'Max', 'Min','Missing'], axis = 1)

    return df

def save_data(df):
    df.to_csv(path_or_buf = 'C:/Users/darrie/Desktop/Data_MET/Output/VST_Setur_MET_QC1.dat')

def main():
    '''Import the data and organize'''
    df = read_data()
    cols  = ['t', 'rh', 'SH_100']

    for col in cols:

        '''Get the configurations'''
        Param = Param_dict_rev[col]
        Config_dict = read_config(Param)

        '''Run the QC'''
        df = QC1_Flag(df, Param, Config_dict)

    print(df)

    '''Save the data'''
    save_data(df)


#run the main
main()
