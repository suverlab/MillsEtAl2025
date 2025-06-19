"""
This file contains functions to source antennal angle information from DeepLabCut,
Transform said angle information into useful formats, and save as a pandas DataFrame.    

Acknowledgments to Marie Suver and Olivia Nunn- Bits of code have been sourced from their previous work
"""

# Dependencies
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
pd.options.mode.chained_assignment = None
import os
import cv2
from skimage.draw import disk
from pathlib import Path
from deeplabcut.utils import auxiliaryfunctions
from scipy.signal import hilbert, butter, filtfilt, firls, savgol_filter, lfilter
import emd

import importMat as im
import constants as const
import experimentList as el

# Functions for extracting angles

def getXY_trackedBodyparts(config_path, videofolder, vidName):
    cfg = auxiliaryfunctions.read_config(config_path)
    bodyparts = cfg['bodyparts']

    #read in tracking data frame
    trainFraction = cfg['TrainingFraction'][0]
    DLCscorer = auxiliaryfunctions.GetScorerName(cfg,1,trainFraction)[0] #automatically loads corresponding model (even training iteration based on snapshot index)
    dataname = str(videofolder)+'/'+vidName+DLCscorer + '.h5'
    if os.path.isfile(dataname):
        Dataframe = pd.read_hdf(dataname)
    else:
        return [], []
    nframes = len(Dataframe.index)
    df_likelihood = np.empty((len(bodyparts),nframes))
    df_x = np.empty((len(bodyparts),nframes))
    df_y = np.empty((len(bodyparts),nframes))
    for bpind, bp in enumerate(bodyparts):
        df_likelihood[bpind,:]=Dataframe[DLCscorer][bp]['likelihood'].values
        df_x[bpind,:]=Dataframe[DLCscorer][bp]['x'].values
        df_y[bpind,:]=Dataframe[DLCscorer][bp]['y'].values

    return df_x, df_y


def get_head_axis(expt = '2024_04_19_E4', cameraView = "dorsal", frameNumToPlot = 20, TEST = 0):

    trialNum = '01'#2 #base head axis on first video
     #frames to plot head axis on (single or average across)
    videotype = 'avi'

    if (cameraView == 'dorsal'):
        vidName = expt+'_Video_Dorsal_'+trialNum
        config_path = const.config_path['dorsal']
        videofolder = const.baseDirectory+'data/data_dorsal'
    elif (cameraView == 'lateral'):
        vidName = expt+'_Video_Lateral_'+trialNum
        config_path = const.config_path['lateral']
        videofolder = const.baseDirectory+'data/data_lateral'

    video_path = videofolder+'/'+vidName+'.'+videotype
    cfg = auxiliaryfunctions.read_config(config_path)
    bodyparts = cfg['bodyparts']

    df_x, df_y = getXY_trackedBodyparts(config_path, videofolder, vidName)

    # compute and plot head axis coordinates
    markers = const.headAxisMarkers[cameraView]
    xant = np.mean([np.mean(df_x[markers[0][0]]),np.mean(df_x[markers[1][0]])])
    yant = np.mean([np.mean(df_y[markers[0][0]]),np.mean(df_y[markers[1][0]])])
    xpost = np.mean([np.mean(df_x[markers[0][1]]),np.mean(df_x[markers[1][1]])])
    ypost = np.mean([np.mean(df_y[markers[0][1]]),np.mean(df_y[markers[1][1]])])
    
    #option to plot tracked points and head axis for one frame
    if TEST:
        colormap = const.colormap
        colorclass=plt.cm.ScalarMappable(cmap=colormap)
        C=colorclass.to_rgba(np.linspace(0,1,len(bodyparts)))
        colors=(C[:,:3]*255).astype(np.uint8)
        capVid = cv2.VideoCapture(video_path)
        print(video_path)
        capVid.set(1,frameNumToPlot)
        ret, frame = capVid.read() #read the frame
        ny = capVid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        nx= capVid.get(cv2.CAP_PROP_FRAME_WIDTH)

        for bpind, bp in enumerate(bodyparts):
            xc = int(df_x[bpind,frameNumToPlot])
            yc = int(df_y[bpind,frameNumToPlot])
            rr, cc = disk((yc,xc),const.dotsize_bodypart,shape=(ny,nx))
            frame[rr, cc, :] = colors[bpind]

        fig, ax = plt.subplots(facecolor=(0.1,0.1,0.1),figsize=(20,18))
        #plot head axis points
        ax.plot(xant, yant,marker='o',color='white',markersize='2')
        #ax.plot(xant, yant+50,marker='o',color='pink',markersize='1')
        ax.plot(xpost, ypost,marker='o',color='white',markersize='2')
        #draw and lengthen head axis for easier visualization!
        rise = (yant-ypost)
        run = (xant-xpost)
        extAnt = 3
        extPost = 5
        if (cameraView == 'frontal'):
            extAnt = 3
            extPost = 5
        ax.plot([xant+run*extAnt,xpost-run*extPost],[yant+rise*extAnt,ypost-rise*extPost],linewidth=1,color='white', linestyle='--')
        plt.title('Defining head axis!',color='white')
        ax.imshow(frame)
        plt.pause(0.001)
        plt.show(block=False)
        plt.show()
    else:
        ax = []
    return [xant, yant, xpost, ypost, ax, plt]


def compute_angles(xant,yant,xpost,ypost,df_x,df_y,frameNumsToComputeAngle,angpairs,ax,cfg, frameNumToPlot, cameraView):
    # TEST = 1
    wid = len(angpairs)
    length = len(frameNumsToComputeAngle)
    angles = np.zeros((length,wid))

    # iterate over each pair of interest and compute its angle relative to the midline of the head
    for ii in range(len(angpairs)):
        pairind = angpairs[ii]
        bpind1 = pairind[0]
        bpind2 = pairind[1]
        for frameInd in range(len(frameNumsToComputeAngle)):
            frameNum = frameNumsToComputeAngle[frameInd]
            x1 = int(df_x[bpind1,frameNum])
            y1 = int(df_y[bpind1,frameNum])
            bodyparts = cfg['bodyparts']
            part = bodyparts[bpind1] #grab name of bodypart (determine if left/right)
            x2 = int(df_x[bpind2,frameNum])
            y2 = int(df_y[bpind2,frameNum])
            #compute angle of part relative to midline - positive values move away from midline
            x4, y4 = xant, yant
            x3, y3 = xpost, ypost

            #compute relative to anterior (e.g. downward antennal deflection produces l and r positive values)
            if part[0] == 'L':
                ang1 = np.arctan2((y2-y1), (x2-x1))
                angHeadAxis = np.arctan2((y4-y3), (x4-x3))
                angRad = np.abs(angHeadAxis)-np.abs(ang1)
            else:
                ang1 = np.arctan2((y1-y2), (x1-x2))
                angHeadAxis = np.arctan2((y3-y4), (x3-x4))
                if (cameraView == "dorsal"):
                    angRad = -(np.abs(ang1)-np.abs(angHeadAxis))
                else:
                    angRad = np.abs(ang1)-np.abs(angHeadAxis)

            angDeg = round(angRad*(180/np.pi),1)
            angles[frameInd][ii] = angDeg * const.upsideDownData
    return angles


def get_antenna_angles(expt = '2024_04_19_E4', cameraView = 'dorsal', trialNum = 3, TEST = 0):
    frameNumToPlot = 4#400
    #grab head axis and plot
    [xant, yant, xpost, ypost, ax, plt] = get_head_axis(expt, cameraView, frameNumToPlot, TEST)

    if trialNum < 10:
        trialNum = '0' + str(trialNum)
        
    videotype = 'avi'
    if (cameraView == 'dorsal'):
        vidName = expt+'_Video_Dorsal_'+str(trialNum)
        videofolder = const.data_path['dorsal']
    elif (cameraView == 'lateral'):
        vidName = expt+'_Video_Lateral_'+str(trialNum)
        videofolder = const.baseDirectory+'videodata/videos_lateral'

    config_path = const.config_path[cameraView]
    cfg = auxiliaryfunctions.read_config(config_path)
    bodyparts = cfg['bodyparts']

    [df_x, df_y] = getXY_trackedBodyparts(config_path, videofolder, vidName)
    #if df_x == []:
        #return []

    nframes = len(df_x[0])
    frameNumsToComputeAngle = list(range(0,nframes))
    angPairs = const.angPairs[cameraView]
    angles = compute_angles(xant,yant,xpost,ypost,df_x,df_y,frameNumsToComputeAngle,angPairs,ax,cfg, frameNumToPlot, cameraView)

    return angles


def get_antenna_angles_adjusted(expt, cameraView, trialNum):
    angles = get_antenna_angles(expt, cameraView, trialNum)
    new_angs = []
    for antennalAvgIDXs in const.angPairAverageSets['dorsal']:
        new_angs.append(np.mean(np.transpose([angles[:,i] for i in antennalAvgIDXs]),axis=1))
    return np.transpose(np.array(new_angs))
    # NOT IMPLEMENTED... look at former function in plotting.py for reference


def getFlightBoolean(trial):
    pad_val=100000
    pad = np.zeros((1,pad_val))
    front_padded = np.append(pad,trial)
    trace_padded = np.append(front_padded,pad)
    amp = np.abs(hilbert(trace_padded))
    b,a = butter(2,6,fs=const.fs)
    fin = filtfilt(b,a,amp)
    out2 = fin[pad_val:-pad_val]
    value = const.smoothed_flight_cutoff_value
    flightBool = out2 > value
    
    """s = np.squeeze(trial)
    alpha=0.9995
    out = [0]
    for sample in s:
        out.append(min(sample, alpha*out[-1]))
    out = out[1:]
    coeff = firls(15, [0, .4, .6, 1], [1,1,0,0])
    out2 = 1.06*filtfilt(coeff,1,out)
    if const.upsideDownHutchens:
        flightBool = out2 < const.smoothed_flight_cutoff_value
    elif const.upsideDownHutchens == False:
        flightBool = out2 > const.smoothed_flight_cutoff_value
    np.sum(flightBool[0:100])
    if (np.sum(flightBool[0:int(const.fs/100)]) / (const.fs/100)) > 0.2: # Due to restrictions on method for determining flight, if 20% of the first 10 ms are counted as flight the whole section is counted.
        flightBool[0:int(const.fs/100)] = True
    """
    return flightBool


def getWBF(flightBool, filtered_data):
    df = pd.DataFrame(columns=[1])
    df['temp'] = filtered_data.apply(lambda row: emd.spectra.frequency_transform(row, 20000, 'nht'))
    b, a = butter(3, 2,fs=const.fs)
    df['temp2'] = df['temp'].apply(lambda row: filtfilt(b,a,np.squeeze(row[1])))
    
    df['wbf'] = np.multiply(df['temp2'],flightBool)
    
    return df['wbf']


def wbaCreate(row):
    wba = np.zeros((const.fs*const.lenVideo,1))
    sample_win = int(const.fs/100)
    for i in range(0,const.fs*const.lenVideo,sample_win):
        if const.upsideDownHutchens:
            wba[i:i+sample_win] = np.min(row[i:i+sample_win])
        else:
            wba[i:i+sample_win] = np.max(row[i:i+sample_win])
    return wba

def wbabaseCreate(row):
    wba = np.zeros((const.fs*const.lenVideo,1))
    sample_win = int(const.fs/100)
    for i in range(0,const.fs*const.lenVideo,sample_win):
        if const.upsideDownHutchens:
            wba[i:i+sample_win] = np.max(row[i:i+sample_win])
        else:
            wba[i:i+sample_win] = np.min(row[i:i+sample_win])
    return wba


def getWBA(flightBool, raw_data):
    dfa = pd.DataFrame(columns=[1])
    dfa['tempwba'] = raw_data.apply(lambda row: wbaCreate(row))
    dfa['tempwbabase'] = raw_data.apply(lambda row: wbabaseCreate(row))
    fbl = np.array(flightBool.tolist())
    tmpwba = np.array(np.squeeze(dfa['tempwba'].tolist()))
    tmpbasewba = np.array(np.squeeze(dfa['tempwbabase'].tolist()))
    fin = list(np.abs(np.multiply(fbl, tmpwba) - np.multiply(fbl, tmpbasewba)))
    dfa['wba'] = pd.Series(dtype='object')
    dfa['wba'] = fin
    
    return dfa['wba']


def getFilteredSignal(df, filtered_data_name, override=False):
    raw_sigs = df[const.raw_signal_name].tolist()
    raw_sigs_plus_fat = [np.concatenate((sig[0:1000],sig)) for sig in raw_sigs]
    div = const.fs / 2
    b, a = butter(2, [150/div, 250/div], btype='band')
    butter_sigs = [lfilter(b, a, np.squeeze(sig)) for sig in raw_sigs_plus_fat]
    filtered_sigs = [savgol_filter(sig,round(const.fs/425.5),2) for sig in butter_sigs]
    if not override:
        df[filtered_data_name] = pd.Series(dtype='object')
    filtered_sigs_without_fat = [sig[1000:] for sig in filtered_sigs]
    df[filtered_data_name] = filtered_sigs_without_fat
    return df
    
def getFlightData(df):
    if const.PRE_FILTERED == False:
        filtered_data_name = 'tachometerSignal_smoothed'
        df = getFilteredSignal(df, filtered_data_name)
    elif const.PRE_FILTERED == True:
        filtered_data_name = const.filtered_data_name
        if const.FILTER_OVERRIDE:
            df = getFilteredSignal(df, filtered_data_name, override=True)
    df['flightBool'] = [getFlightBoolean(trial) for trial in df[filtered_data_name]]
    df['wbf'] = getWBF(df['flightBool'],df[filtered_data_name])
    df['wba'] = getWBA(df['flightBool'],df[const.raw_signal_name])
    
    return df
    
    
def getAntennalData(experiment, cameraView, df):
    
    df['L_antenna'] = pd.Series(dtype='object')
    df['R_antenna'] = pd.Series(dtype='object')
    df['iaa'] =  pd.Series(dtype='object')
    
    left_angles, right_angles, iaa = [], [], []
    l_start_idx = const.angPairs_byAntenna[cameraView][0][0]
    l_end_idx = const.angPairs_byAntenna[cameraView][0][1]
    r_start_idx = const.angPairs_byAntenna[cameraView][1][0]
    r_end_idx =  const.angPairs_byAntenna[cameraView][1][1]
    for i in df.index:
        if const.TRIAL_NUMS_IN_MAT == True:
            j = df[const.trial_num_name][i][0]
        elif const.TRIAL_NUMS_IN_MAT == False:
            j = i + 1
        if const.ANGPAIR_AVGS == True:
            a = get_antenna_angles_adjusted(experiment, cameraView, j)
            l_a = a[:,l_start_idx:l_end_idx+1]
            r_a = a[:,r_start_idx:r_end_idx+1]
        elif const.ANGPAIR_AVGS == False:
            a = get_antenna_angles(experiment, cameraView, j)
            l_a = a[:,l_start_idx:l_end_idx+1]
            r_a = a[:,r_start_idx:r_end_idx+1]
            
        left_angles.append(l_a)
        right_angles.append(r_a)
        iaa.append(np.add(l_a,r_a))
    
    df['L_antenna'] = left_angles
    df['R_antenna'] = right_angles
    df['iaa'] = iaa
    
    return df

# This function will need to be edited more in the future, branching ifs here to determine conditional avgs.
# Currently Suppored: Multiple Sequences, Multiple Stimuli
def getConditionalAvgs(df):
    if const.ONE_STIM == False:
        if const.MULT_SEQ == True:
            if const.FLIGHT:
                fnf = ['_Flight', '_noFlight']
                flightNames = [stim + fnf[0] for stim in const.stimNames]
                noflightNames = [stim + fnf[1] for stim in const.stimNames]
                for idx, name in enumerate(flightNames):
                    df[name] = pd.Series(dtype='object')
                    df[noflightNames[idx]] = pd.Series(dtype='object')
            for i in df.index:
                traces = df['iaa'][i]
                if const.ANGPAIR_AVGS == True:
                    avgs = np.zeros((len(const.stimNames),np.shape(traces)[1]))
                elif const.ANGPAIR_AVGS == False:
                    avgs = np.zeros((len(const.stimNames),np.shape(traces)[1]))
                stimType = const.stimSeqNames[const.stimSeqNumbers.index(df[const.seq_order_name][i][0])]
                stimSeq = const.stimSeqs[stimType]
                if const.FLIGHT:
                    flightBool = df['flightBool'][i]
                    if const.PUFFER:
                        pufferSignal = df[const.puffer_signal_name][i]
                    flyingBool = np.zeros(np.shape(avgs))
                    not_flyingBool = np.zeros(np.shape(avgs))
                for j, stim in enumerate(stimSeq):
                    stim_save_idx = const.stimNames.index(stim)
                    avgStart = const.stimStart[j] + const.avgStartAndLen[j][0]
                    avgEnd = avgStart + const.avgStartAndLen[j][1]
                    avgs[stim_save_idx, :] = np.mean(traces[avgStart*const.fps:avgEnd*const.fps,:], axis=0)
                    if const.FLIGHT:
                        if np.all(flightBool[avgStart*const.fs:avgEnd*const.fs]):
                            flyingBool[stim_save_idx,:] = True
                        elif np.all(flightBool[avgStart*const.fs:avgEnd*const.fs] == False):
                            not_flyingBool[stim_save_idx,:] = True
                        if const.PUFFER:
                            if np.any(pufferSignal[avgStart*const.fs:avgEnd*const.fs] > const.puffer_cutoff_value):
                                flyingBool[stim_save_idx,:] = False
                                not_flyingBool[stim_save_idx,:] = False
                            
                if const.FLIGHT:
                    flyingArray = avgs * flyingBool
                    flyingArray[flyingArray == 0] = np.nan
                    not_flyingArray = avgs * not_flyingBool
                    not_flyingArray[not_flyingArray == 0] = np.nan
                    for k in range(len(flyingArray)):
                        df[flightNames[k]][i] = flyingArray[k,:]
                        df[noflightNames[k]][i] = not_flyingArray[k,:]
    elif const.ONE_STIM == True: # In this condition, flight must occur during whole trial length to be counted (baseline is intrinsically linked to stimulus)
        if const.FLIGHT == True and const.BASELINE == False:
            catgs = ['StimAvg_Flight', 'StimAvg_noFlight']
            df[catgs[0]] = pd.Series(dtype='object')
            df[catgs[1]] = pd.Series(dtype='object')
        elif const.FLIGHT == True and const.BASELINE == True:
            catgs = ['BaseAvg_Flight', 'StimAvg_Flight', 'BaseAvg_noFlight', 'StimAvg_noFlight']
            df[catgs[0]] = pd.Series(dtype='object')
            df[catgs[1]] = pd.Series(dtype='object')
            df[catgs[2]] = pd.Series(dtype='object')
            df[catgs[3]] = pd.Series(dtype='object')
        elif const.FLIGHT == False and const.BASELINE == False:
            catgs = ['StimAvg'] # Not implemented
        elif const.FLIGHT == False and const.BASELINE == True:
            catgs = ['BaseAvg', 'StimAvg']
            
        for i in df.index:
            traces = df['iaa'][i]
            if const.STIM:
                stimEnd = const.stimEnd
            if const.BASELINE:
                baseEnd = const.baselineEnd
            if const.FLIGHT:
                flightBool = df['flightBool'][i]
                if const.PUFFER:
                    pufferSignal = df[const.puffer_signal_name][i]
            if const.FLIGHT == True and const.BASELINE == True:
                if np.all(flightBool): #full flight
                    df[catgs[0]][i] = np.mean(traces[const.baselineStart*const.fps:baseEnd*const.fps,:], axis=0)
                    df[catgs[1]][i] = np.mean(traces[const.stimStart*const.fps:stimEnd*const.fps,:], axis=0)
                    df[catgs[2]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[3]][i] = np.tile(np.nan,np.shape(traces)[1])
                elif np.all(flightBool == False): #full no flight
                    df[catgs[0]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[1]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[2]][i] = np.mean(traces[const.baselineStart*const.fps:baseEnd*const.fps,:], axis=0)
                    df[catgs[3]][i] = np.mean(traces[const.stimStart*const.fps:stimEnd*const.fps,:], axis=0)    
                else:
                    df[catgs[0]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[1]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[2]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[3]][i] = np.tile(np.nan,np.shape(traces)[1])
                if const.PUFFER:
                    if np.any(pufferSignal[const.stimStart*const.fs:stimEnd*const.fs] > const.puffer_cutoff_value):
                        df[catgs[0]][i] = np.tile(np.nan,np.shape(traces)[1])
                        df[catgs[1]][i] = np.tile(np.nan,np.shape(traces)[1])
                        df[catgs[2]][i] = np.tile(np.nan,np.shape(traces)[1])
                        df[catgs[3]][i] = np.tile(np.nan,np.shape(traces)[1])
            elif const.FLIGHT == True and const.BASELINE == False:
                if np.all(flightBool): #full flight
                    df[catgs[0]][i] = np.mean(traces[const.stimStart*const.fps:stimEnd*const.fps,:], axis=0)
                    df[catgs[1]][i] = np.tile(np.nan,np.shape(traces)[1])
                elif np.all(flightBool == False): #full no flight
                    df[catgs[1]][i] = np.mean(traces[const.stimStart*const.fps:stimEnd*const.fps,:], axis=0)
                    df[catgs[0]][i] = np.tile(np.nan,np.shape(traces)[1])
                else:
                    df[catgs[0]][i] = np.tile(np.nan,np.shape(traces)[1])
                    df[catgs[1]][i] = np.tile(np.nan,np.shape(traces)[1])
                if const.PUFFER:
                    if np.any(pufferSignal[const.stimStart*const.fs:stimEnd*const.fs] > const.puffer_cutoff_value):
                        df[catgs[0]][i] = np.tile(np.nan,np.shape(traces)[1])
                        df[catgs[1]][i] = np.tile(np.nan,np.shape(traces)[1])
                    
    return df
                    

# CREATES DATAFRAME BASED ON SPECIFIED PARAMETERS IN constants.py
def createDataFrame(cameraView='dorsal'):
    df_arr = []
    for condition in el.all_notes:
        flynum = 0
        if len(condition) > 0:
            for experiment in condition:
                df_fly = im.importMat(const.matDirectory + experiment + '.mat')
                df_fly['fly'] = pd.Series(dtype='int')
                df_fly['fly'] = [flynum] * const.numTrials
                flynum += 1
                if const.FLIGHT: # Add flight data
                    df_fly = getFlightData(df_fly)
                if const.WALKING: # Add walking data
                    print('not implemented...')
                # Add Antennal Angle Data    
                df_fly = getAntennalData(experiment, cameraView, df_fly)
                if const.STIM: # Add stimulus Data if averages are wanted
                    df_fly = getConditionalAvgs(df_fly)
                print(experiment +' added to Dataframe.')
                df_arr.append(df_fly)
                    
        elif len(condition) < 0:
            print('Condition ' + str(condition) + ' is empty! Skipping...')
    
    df = pd.concat(df_arr)
    df.to_pickle(const.savedDataFrameDirectory+cameraView+'_DataFrame.pkl')
    return df


