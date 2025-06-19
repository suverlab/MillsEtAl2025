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
    condtionalAvgs = np.array([np.vstack(df.query('fly==@i')[col_name].tolist()) for i in range(df['fly'].max()+1)])
    return condtionalAvgs