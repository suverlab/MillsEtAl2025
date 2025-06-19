"""
This file holds all experiment names to be analyzed and used in angleDataframeCreation.py and plottingFunctions.py.
    
"""

# For each condition, create a list with each experiment in said condition and put the name in
# all_notes and all_notes_names (as a string) respectively.
Wind = [
    '2024_09_27_E2', #0
    '2024_09_30_E1', #1
    '2024_10_03_E1', #2
    '2024_10_03_E2', #3
    '2024_10_18_E3', #4
    '2024_10_18_E6', #5
    '2024_10_25_E1', #6
    '2024_10_28_E3', #7
    '2024_10_28_E5', #8
    '2024_10_30_E1', #9
    '2024_10_30_E2', #10
    '2024_10_31_E1', #11
    '2024_11_01_E4', #12
    '2024_11_01_E5', #13
    '2024_11_01_E8' #14
]

Visual = [
    '2024_09_27_E1', #0
    '2024_09_30_E2', #1
    '2024_10_03_E3', #2
    '2024_10_03_E4', #3
    '2024_10_17_E2', #4
    '2024_10_18_E4', #5
    '2024_10_25_E3', #6
    '2024_10_28_E1', #7
    '2024_10_28_E7', #8
    '2024_10_30_E4', #9
    '2024_10_31_E3', #10
    '2024_10_31_E5', #11
    '2024_11_01_E3', #12
    '2024_11_01_E7', #13
    '2024_11_01_E9' #14
]

Both = [
    '2024_09_26_E1', #0
    '2024_09_27_E3', #1
    '2024_09_30_E3', #2
    '2024_10_17_E1', #3
    '2024_10_18_E2', #4
    '2024_10_25_E2', #5
    '2024_10_25_E4', #6
    '2024_10_28_E2', #7
    '2024_10_28_E4', #8
    '2024_10_30_E3', #9
    '2024_10_31_E2', #10
    '2024_10_31_E4', #11
    '2024_11_01_E2', #12
    '2024_11_01_E6', #13
    '2024_11_01_E10' #14
]

Neither = [
    '2024_09_27_E4', #0
    '2024_10_18_E1', #4
    '2024_10_18_E5', #4
    '2024_10_28_E6', #4
    '2024_11_01_E1' #4
]

all_notes = [Wind, Visual, Both, Neither]
all_notes_names = ['Wind','Visual', 'Both', 'Neither']
num_experiments = sum([len(condition) for condition in all_notes])