"""
This file transforms .mat files into useable pandas dataframes.

Acknowledgments to Marie Suver and Olivia Nunn- Bits of code have been sourced from their previous work
"""
# CHANGE ALL VALUES TO VALUES FOUND WITHIN MAT FILE.

# Dependencies

import numpy as np
import scipy.io as spio
import pandas as pd
import constants as const

def importMat(file_path = const.matDirectory):
    
    nn = spio.loadmat(file_path)
    
    list_values = [v for v in nn.values()]
    list_values = list_values[3]
    
    date = []
    expnumber = [] 
    condition = []
    min_age = []
    max_age = []
    samplerate = []
    fps = []
    nframes = []
    trialLength = []
    block = []
    block_trial = []
    trialnum = []
    pufferSignal = []
    stimulus = []
    ampCondition = []
    tachometerSignal = []
    tachometerSignal_smoothed = []
    photodiodeSignal = []
        
    # Iteratively store each of your items here
    # Change names of variables to match .mat structure!
    # SIMPLE THINGS (e.g. trial one) - format as expt[number][0]
    # VECTORS WITH NO TRIM (e.g a tachometer signal) - format as expt[number][:]
    # VECTORS WITH TRIMMING! see constants.py (e.g. a tachometer signal where video starts later) - format as np.delete(expt[number], trim)
    if const.TRIM:
        trimstart = const.trimStart * const.fs
        trimend = trimstart + (const.trimLen * const.fs)
        trim = list(range(trimstart,trimend))
    
    for ind in range(len(list_values[0,:])):
        expt = list_values[0,ind]

        date.append(expt[0][0])
        expnumber.append(expt[1][0])
        condition.append(expt[2][0])
        min_age.append(expt[3][0])
        max_age.append(expt[4][0])
        samplerate.append(expt[5][0])
        fps.append(expt[6][0])
        nframes.append(expt[7][0])
        trialLength.append(expt[8][0])
        block.append(expt[9][0])
        block_trial.append(expt[10][0])
        trialnum.append(expt[11][0])
        stimulus.append(expt[12][0])
        #ampCondition.append(expt[13][0])
        if const.TRIM:
            pufferSignal.append(np.delete(expt[13], trim, axis=0))
            tachometerSignal.append(np.delete(expt[14], trim, axis=0))
            photodiodeSignal.append(np.delete(expt[15], trim, axis=0))
        else:
            pufferSignal.append(expt[13][:])
            tachometerSignal.append(expt[14][:])
            photodiodeSignal.append(expt[15][:])
            
        dd = {'date':date,
              'expnumber':expnumber,
              'condition':condition,
              'min_age':min_age,
              'max_age':max_age,
              'samplerate':samplerate,
              'fps':fps,
              'nframes':nframes,
              'trialLength':trialLength,
              'block':block,
              'block_trial':block_trial,
              'trialnum':trialnum,
              'stimulus':stimulus,
              #'ampCondition':ampCondition,
              'pufferSignal':pufferSignal,
              'tachometerSignal':tachometerSignal,
              'photodiodeSignal':photodiodeSignal
              }

        notes = pd.DataFrame(data=dd)
            
    return notes