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

# This function returns a strip plot containing the average by fly for each column fed in. Colors ar 
def basicStripPlot(col_list, ang_pair_idx=0, catg_names=None, xlabel='Wind Speed (cm/s)', ylabel='IAA (deg)', title='IAA across windspeeds, Flight', df=pd.DataFrame()):
    if catg_names == None or len(catg_names) != len(col_list):
        print('No category names inputted or number of inputted categories does not match number of columns. Defaulting...')
        catg_names = col_list
    strip_df = pd.DataFrame()
    for i, col in enumerate(col_list):
        strip_df[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,ang_pair_idx]
    fig, ax = plt.subplots()
    sns.stripplot(data=strip_df,ax=ax)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    
    
def LinePlot2ndSeg3rdSeg(col_list, savename, catg_names=None, diffPlot = False,  xlabel='Wind Speed (cm/s)', ylabel='IAA (deg)', title='IAA across windspeeds, Flight', df=pd.DataFrame()):
    if catg_names == None or len(catg_names) != len(col_list):
        print('No category names inputted or number of inputted categories does not match number of columns. Defaulting...')
        catg_names = col_list
    line_df_2nd = pd.DataFrame()
    line_df_3rd = pd.DataFrame()
    for i, col in enumerate(col_list):
        line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,1] - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,1]
        line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,0] - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,0]

    df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
    df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

    df_2nd['Antennal Segment'] = '2nd Segment'
    df_2nd['index'] = df_2nd.index
    df_3rd['Antennal Segment'] = '3rd Segment'
    df_3rd['index'] = df_3rd.index
    
    if diffPlot == False:
        df_plot = pd.concat([df_2nd, df_3rd]).reset_index()
        fig, ax = plt.subplots()
        sns.lineplot(x='windspeed',y='iaa',hue='Antennal Segment', units=df_plot['index'], data=df_plot, ax=ax, marker='o', linewidth=0.8, estimator=None)
    elif diffPlot == True:
        df_plot = df_2nd.copy(deep=True)
        df_plot['iaa'] = df_3rd['iaa'] - df_2nd['iaa']
        df_plot = df_plot.reset_index()
        fig, ax = plt.subplots()
        sns.lineplot(x='windspeed',y='iaa', units=df_plot['index'], data=df_plot, ax=ax, marker='o', linewidth=0.8, estimator=None)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_ylim([-30, 30])
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(direction="in")
    
    fig.savefig(const.savedFigureDirectory+'png/'+savename+'.png',format='png')
    fig.savefig(const.savedFigureDirectory+savename+'.pdf',format='pdf')
    
def LinePlotBothAntenna(col_list_1, col_list_2, savename, catg_names=None, xlabel='Wind Speed (cm/s)', ylabel='Change in Antennal Angle (deg)', title='IAA across windspeeds, Flight', absolute=False, df=pd.DataFrame()):
    fig, ax = plt.subplots()
    for p, col_list in enumerate([col_list_1, col_list_2]):
        if catg_names == None or len(catg_names) != len(col_list):
            print('No category names inputted or number of inputted categories does not match number of columns. Defaulting...')
            catg_names = col_list
        line_df_2nd = pd.DataFrame()
        line_df_3rd = pd.DataFrame()
        for i, col in enumerate(col_list):
            if absolute:
                line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,1] #- np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,1]
                line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,0] #- np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,0]
            else:
                line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,1] - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,1]
                line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,0] - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,0]
        df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
        df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

        palette = [[const.blue, const.orange], [const.teal, const.red]]
        if p == 0:
            df_2nd['Antennal Segment'] = 'Left 2nd Segment'
            df_2nd['index'] = df_2nd.index
            df_3rd['Antennal Segment'] = 'Left 3rd Segment'
            df_3rd['index'] = df_3rd.index
        elif p == 1:
            df_2nd['Antennal Segment'] = 'Right 2nd Segment'
            df_2nd['index'] = df_2nd.index
            df_3rd['Antennal Segment'] = 'Right 3rd Segment'
            df_3rd['index'] = df_3rd.index
            
        df_plot = pd.concat([df_2nd, df_3rd]).reset_index()
    
        sns.lineplot(x='windspeed',y='iaa',hue='Antennal Segment', data=df_plot, ax=ax, palette=palette[p])
    
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    if absolute:
        ax.set_ylim([45, 90])
    else:
        ax.set_ylim([-10, 30])
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(direction="in")
    if absolute:
        fig.savefig(const.savedFigureDirectory+'png/'+savename+'_absolute'+'.png',format='png')
        fig.savefig(const.savedFigureDirectory+savename+'_absolute'+'.pdf',format='pdf')
    else:
        fig.savefig(const.savedFigureDirectory+'png/'+savename+'.png',format='png')
        fig.savefig(const.savedFigureDirectory+savename+'.pdf',format='pdf')
        
def LinePlotAntennaIaa(col_list, savename, catg_names=None, xlabel='windspeed (cm/s)', ylabel='change in inter-antennal angle (deg)', title='inter-antennal angle across windspeeds, flight', absolute=False, df=pd.DataFrame()):
    fig, ax = plt.subplots()
    if catg_names == None or len(catg_names) != len(col_list):
        print('No category names inputted or number of inputted categories does not match number of columns. Defaulting...')
        catg_names = col_list
    line_df_2nd = pd.DataFrame()
    line_df_3rd = pd.DataFrame()
    for i, col in enumerate(col_list):
        if absolute:
            line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,1] # - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,1]
            line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,0] # - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,0]
        else:
            line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,1] - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,1]
            line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df), axis=1)[:,0] - np.nanmean(extractConditionalAvgs(col_list[0], df), axis=1)[:,0]

    df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
    df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

    palette = [const.blue, const.orange]
    df_2nd['Antennal Segment'] = '2nd Segment'
    df_2nd['index'] = df_2nd.index
    df_3rd['Antennal Segment'] = '3rd Segment'
    df_3rd['index'] = df_3rd.index
    
            
    df_plot = pd.concat([df_2nd, df_3rd]).reset_index()
    
    sns.lineplot(x='windspeed',y='iaa',hue='Antennal Segment', data=df_plot, ax=ax, palette=palette,units=df_plot['index'],estimator=None, linewidth=0.8,marker='o')
    
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    # ax.set_ylim([-20, 20])
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(direction="in")
    
    if absolute:
        fig.savefig(const.savedFigureDirectory+'png/'+savename+'_absolute'+'.png',format='png')
        fig.savefig(const.savedFigureDirectory+savename+'_absolute'+'.pdf',format='pdf')
    else:
        fig.savefig(const.savedFigureDirectory+'png/'+savename+'.png',format='png')
        fig.savefig(const.savedFigureDirectory+savename+'.pdf',format='pdf')
    
    
def diffLinePlot(catgs_to_plot, savename, catg_names=None, sampsize=False, xlabel='windspeed (cm/s)', ylabel='difference in inter-antennal angle (deg)', title='passive - active joint angle', absolute=False, df=pd.DataFrame()):
    line_df_2nd = pd.DataFrame()
    line_df_3rd = pd.DataFrame()
    fig, ax = plt.subplots()
    df_plots = []
    j = 0
    df_dark = df[df['condition'] == 'dark']
    df_dead = df[df['condition'] == 'dead']
    df_static = df[df['condition'] == 'static']
    col_list_flight = ['0_Flight', '50_Flight', '100_Flight', '150_Flight', '200_Flight', '250_Flight', '300_Flight']
    col_list_noflight = ['0_noFlight', '50_noFlight', '100_noFlight', '150_noFlight', '200_noFlight', '250_noFlight', '300_noFlight']
    for col_list in [col_list_flight, col_list_noflight]:
        for i, col in enumerate(col_list):
            if absolute:
                line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dark), axis=1)[:,1] #- np.nanmean(extractConditionalAvgs(col_list[0], df_dark), axis=1)[:,1]
                line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dark), axis=1)[:,0] #- np.nanmean(extractConditionalAvgs(col_list[0], df_dark), axis=1)[:,0]
            else:
                line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dark), axis=1)[:,1] - np.nanmean(extractConditionalAvgs(col_list[0], df_dark), axis=1)[:,1]
                line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dark), axis=1)[:,0] - np.nanmean(extractConditionalAvgs(col_list[0], df_dark), axis=1)[:,0]
        df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
        df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

        df_2nd['Antennal Segment'] = '2nd Segment'
        df_2nd['index'] = df_2nd.index
        df_3rd['Antennal Segment'] = '3rd Segment'
        df_3rd['index'] = df_3rd.index
    
        j_list = ['Dark Flight', 'Dark No Flight']
        df_plot = df_2nd.copy(deep=True)
        df_plot['iaa'] = df_3rd['iaa'] - df_2nd['iaa']
        df_plot = df_plot.reset_index(drop=True)
        df_plot['state'] = j_list[j]
        df_plots.append(df_plot)
        j += 1
    # static fly inclusion
    j = 0
    line_df_2nd = pd.DataFrame()
    line_df_3rd = pd.DataFrame()
    for col_list in [col_list_flight, col_list_noflight]:
        for i, col in enumerate(col_list):
            if absolute:
                line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_static), axis=1)[:,1] #- np.nanmean(extractConditionalAvgs(col_list[0], df_dark), axis=1)[:,1]
                line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_static), axis=1)[:,0] #- np.nanmean(extractConditionalAvgs(col_list[0], df_dark), axis=1)[:,0]
            else:
                line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_static), axis=1)[:,1] - np.nanmean(extractConditionalAvgs(col_list[0], df_static), axis=1)[:,1]
                line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_static), axis=1)[:,0] - np.nanmean(extractConditionalAvgs(col_list[0], df_static), axis=1)[:,0]
        df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
        df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

        df_2nd['Antennal Segment'] = '2nd Segment'
        df_2nd['index'] = df_2nd.index
        df_3rd['Antennal Segment'] = '3rd Segment'
        df_3rd['index'] = df_3rd.index
    
        j_list = ['Static Flight', 'Static No Flight']
        df_plot = df_2nd.copy(deep=True)
        df_plot['iaa'] = df_3rd['iaa'] - df_2nd['iaa']
        df_plot = df_plot.reset_index(drop=True)
        df_plot['state'] = j_list[j]
        df_plots.append(df_plot)
        j += 1
        
    # dead fly inclusion
    line_df_2nd = pd.DataFrame()
    line_df_3rd = pd.DataFrame()
    for i, col in enumerate(col_list_noflight):
        if absolute:
            line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dead), axis=1)[:,1] # - np.nanmean(extractConditionalAvgs(col_list[0], df_dead), axis=1)[:,1]
            line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dead), axis=1)[:,0] # - np.nanmean(extractConditionalAvgs(col_list[0], df_dead), axis=1)[:,0]
        else:
            line_df_2nd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dead), axis=1)[:,1] - np.nanmean(extractConditionalAvgs(col_list[0], df_dead), axis=1)[:,1]
            line_df_3rd[catg_names[i]] = np.nanmean(extractConditionalAvgs(col, df_dead), axis=1)[:,0] - np.nanmean(extractConditionalAvgs(col_list[0], df_dead), axis=1)[:,0]

    df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
    df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

    df_2nd['Antennal Segment'] = '2nd Segment'
    df_2nd['index'] = df_2nd.index
    df_3rd['Antennal Segment'] = '3rd Segment'
    df_3rd['index'] = df_3rd.index
    
    df_plot = df_2nd.copy(deep=True)
    df_plot['iaa'] = df_3rd['iaa'] - df_2nd['iaa']
    df_plot = df_plot.reset_index(drop=True)
    df_plot['state'] = 'Dead'
    df_plots.append(df_plot)
 
 
    df_final = pd.concat(df_plots).reset_index()
    df_restricted_list = [] 
    for catg in catgs_to_plot:
        df_restricted_list.append(df_final[df_final['state'] == catg])

    df_restricted = pd.concat(df_restricted_list).reset_index(drop=True)
    
    if len(catgs_to_plot) == 1:
        p = const.HCblue
    elif len(catgs_to_plot) == 2:
        p = [const.HCblue,const.HCyellow]
    elif len(catgs_to_plot) ==3:
        p = [const.HCblue,const.HCyellow,const.HCred]
        
    if sampsize:
        df_restricted = df_restricted.replace(to_replace='Dark Flight', value='Dark Flight (N=30)')
        df_restricted = df_restricted.replace(to_replace='Dark No Flight', value='Dark No Flight (N=29)')
        df_restricted = df_restricted.replace(to_replace='Dead', value='Dead (N=10)')
        df_restricted = df_restricted.replace(to_replace='Static Flight', value='Static Flight (N=23)')
        df_restricted = df_restricted.replace(to_replace='Static No Flight', value='Static No Flight (N=29)')
    
    sns.lineplot(x='windspeed',y='iaa', hue='state', data=df_restricted, ax=ax, palette=p)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    if absolute:
        ax.set_ylim([-30, 30])
    else:
        ax.set_ylim([-10,40])
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(direction="in")
    ax.legend(frameon=False, loc='lower right')
    
    if absolute:
        fig.savefig(const.savedFigureDirectory+'png/'+savename+'_absolute'+'.png',format='png')
        fig.savefig(const.savedFigureDirectory+savename+'_absolute'+'.pdf',format='pdf')
    else:
        fig.savefig(const.savedFigureDirectory+'png/'+savename+'.png',format='png')
        fig.savefig(const.savedFigureDirectory+savename+'.pdf',format='pdf')


def OneExperimentLinePlot2ndSeg3rdSeg(experiment, col_list, catg_names=None,  xlabel='Wind Speed (cm/s)', ylabel='IAA (deg)', title=None, df=pd.DataFrame()):
    if catg_names == None or len(catg_names) != len(col_list):
        print('No category names inputted or number of inputted categories does not match number of columns. Defaulting...')
        catg_names = col_list
    line_df_2nd = pd.DataFrame()
    line_df_3rd = pd.DataFrame()
    for i, col in enumerate(col_list):
        line_df_2nd[catg_names[i]] = np.vstack(df.loc[df['fly'] ==experiment][col].tolist())[:,1] - np.vstack(df.loc[df['fly'] ==0][col_list[0]].tolist())[:,1]
        line_df_3rd[catg_names[i]] = np.vstack(df.loc[df['fly'] ==experiment][col].tolist())[:,0] - np.vstack(df.loc[df['fly'] ==0][col_list[0]].tolist())[:,0]

    df_2nd =pd.melt(line_df_2nd, var_name='windspeed',value_name='iaa',ignore_index=False)
    df_3rd =pd.melt(line_df_3rd, var_name='windspeed',value_name='iaa',ignore_index=False)

    df_2nd['Antennal Segment'] = '2nd Segment'
    df_2nd['index'] = df_2nd.index
    df_3rd['Antennal Segment'] = '3rd Segment'
    df_3rd['index'] = df_3rd.index
    
    df_plot = pd.concat([df_2nd, df_3rd]).reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(x='windspeed',y='iaa',hue='Antennal Segment', units=df_plot['index'], data=df_plot, ax=ax, marker='o', linewidth=0.8, estimator=None)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    if title == None:
        ax.set_title('Fly #' + str(experiment) + ' IAA across windspeeds')
    ax.set_ylim([-40, 40])
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(direction="in")
    
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
        