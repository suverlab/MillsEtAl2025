"""
This file holds all experiment names to be analyzed and used in angleDataframeCreation.py and plottingFunctions.py.
    
"""

# For each condition, create a list with each experiment in said condition and put the name in
# all_notes and all_notes_names (as a string) respectively.

silenced = [
    '2025_01_09_E8', #0
    '2025_01_09_E9', #1
    '2025_01_16_E1', #2
    '2025_01_16_E2', #3
    '2025_01_16_E3', #4
    '2025_01_16_E4', #5
    '2025_01_28_E1', #6
    '2025_01_28_E2', #7
    '2025_01_28_E3', #8
    '2025_01_28_E4', #9
    '2025_01_30_E1', #10
    '2025_01_30_E2', #11
    '2025_01_30_E3', #12
    #'2025_01_30_E4',  excluded, scewed upwards tether angle affecting perspective of movement
    #'2025_01_30_E5',  excluded, scewed upwards tether angle affecting perspective of movement
    #'2025_01_30_E6',  excluded, scewed upwards tether angle affecting perspective of movement
    '2025_01_31_E1', #13
    '2025_01_31_E2', #14
    '2025_01_31_E3', #15
    '2025_01_31_E4' #16
]

silencedCS = [
    '2025_01_07_E5', #0
    '2025_01_09_E1', #1
    '2025_01_09_E2', #2
    '2025_01_09_E3', #3
    '2025_01_09_E4', #4
    '2025_01_09_E5', #5
    '2025_01_09_E6', #6
    '2025_01_09_E7', #7
    '2025_01_13_E7', #8
    '2025_01_13_E8', #9
    '2025_02_27_E1', #10
    '2025_02_27_E2', #11
    '2025_02_27_E3', #12
    '2025_02_27_E4', #13
    '2025_02_27_E5' #14
]

silencedCS_glued = [
    '2025_03_04_E1', #0
    '2025_03_05_E1', #1
    '2025_03_05_E2', #2
    '2025_03_05_E3', #3
    '2025_03_11_E1', #4
    '2025_03_11_E2', #5
    '2025_03_11_E3', #6
    '2025_03_12_E1', #7
    '2025_03_12_E2', #8
    # '2025_03_12_E3', #9 excluded, scewed head fix is affecting perspective of movement
    '2025_03_13_E1', #10
    '2025_03_13_E2', #11
    '2025_03_14_E1', #12
    '2025_03_14_E2', #13
    '2025_03_14_E3', #14
    '2025_03_14_E4' #15
]
 
all_notes = [silenced,silencedCS,silencedCS_glued]
all_notes_names = ['silenced','silencedCS','silencedCS_glued']
num_experiments = sum([len(condition) for condition in all_notes])