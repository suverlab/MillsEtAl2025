"""
This file contains functions to load a pickled DataFrame,
and a variety of functions used to plot data found in said dataframe.

DataFrame is created in angleDataframeCreation.py

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import date
from scipy import signal
import statsmodels.api as sm
import seaborn as sns
from numpy.random import rand
from math import log10, floor
from scipy import stats
import cv2
from skimage.draw import circle_perimeter, disk
from scipy.io import savemat
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

import importMat as im
import constants as const
import experimentList as el
import angleDataframeCreation as adc

# This function loads the previously created dataframe based upon inputted cameraview
def loadDataFrame(cameraView):
    df = pd.read_pickle(const.savedDataFrameDirectory+cameraView+'_DataFrame.pkl')
    return df

# This function returns a numpy array with the following dimensions: (num_experiments, numTrials, numAngPairs)
def extractConditionalAvgs(col_name, df=pd.DataFrame()):
    condtionalAvgs = np.array([np.vstack(df.query('fly==@i')[col_name].tolist()) for i in range(int(df['fly'].max()+1))])
    return condtionalAvgs

def countStats(df):
    flight_cols = ['0_Flight','50_Flight','100_Flight','150_Flight','200_Flight','250_Flight','300_Flight']
    no_flight_cols = ['0_noFlight','50_noFlight','100_noFlight','150_noFlight','200_noFlight','250_noFlight','300_noFlight']
    all_cols = [flight_cols, no_flight_cols]

    for col_list in all_cols:
        for condition in df['condition'].unique():
            print('Condition: ' + condition)
            N_list = []
            n_list = []
            for col in col_list:
                nanBool = ~np.isnan(np.nanmean(extractConditionalAvgs(col,df[df['condition'] == condition]),axis=2))
                N = np.sum(np.count_nonzero(nanBool, axis=1) > 0)
                n = np.sum(np.count_nonzero(nanBool, axis=1))
                print(col + ': ' + 'N= ' + str(N) + ' ' + 'n= ' + str(n))
                N_list.append(N)
                n_list.append(n)
            print()
            print('Number of flies for condition: ' + str(np.max(N_list)))
            print()
        