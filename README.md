## README.md - Mills et al. 2025 - Multisensory integration for active mechanosensation in _Drosophila_ flight

### Folders correspond to the following figures-  

**WindyStepsAnalysis**- Fig 2-4  
**SpeedyBarsAnalysis**- Fig 5  
**CocoAnalysis**- Fig 6  
**wbaAnalysis** -  Fig S1  
**prelimCocoAnalysis**- Fig S4  

### Descriptions of each file
**angleDataframeCreation.py** - This file takes raw data (typically an experimental .mat file alongside tracked DeepLabCut data) and performs postprocessing steps.
This includes smoothing the wingbeat sensor signal (in order to pull out frequency information) and calculating the angle of the antennae over time. Processed data
is then saved in a pandas DataFrame as a .pkl file.  

**plottingFunctions.py** - This file includes code to load processed data and to extract averages by condition, sometimes used in code found within jupyter notebooks  

**constants.py** - This file includes constants used in all other python code, including the jupyter notebook. NOTE: This is where file paths must be changed to match your directory setup!  

**experimentList.py** - This file includes the name of each experiment, sorted by condition. This file is required to generate the processed data (see angleDataframeCreation.py)  

**importMat.py** - This file imports experimental data from each .mat file (each .mat file is one experimental fly). Used in angleDataframeCreation.py

**Jupyter Notebooks** - This is where all analysis, figuremaking, etc. occurs.
