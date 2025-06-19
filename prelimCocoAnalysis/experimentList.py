"""
This file holds all experiment names to be analyzed and used in angleDataframeCreation.py and plottingFunctions.py.
    
"""

# For each condition, create a list with each experiment in said condition and put the name in
# all_notes and all_notes_names (as a string) respectively.
Wind = [
    '2024_08_28_E1', #0
    '2024_08_29_E1', #1
    '2024_08_29_E5', #2
    '2024_08_30_E3', #3
    '2024_08_30_E6', #4
    '2024_08_30_E7', #5
    '2024_09_03_E3', #6
    '2024_09_03_E7', #7
    '2024_09_03_E9' #8
]

Visual = [
    '2024_08_28_E2', #0
    '2024_08_29_E4', #1
    '2024_08_30_E1', #2
    '2024_08_30_E4', #3
    '2024_08_30_E8', #4
    '2024_09_03_E5', #5
    '2024_09_03_E8' #6
]

Both = [
    '2024_08_29_E2', #0
    '2024_08_29_E3', #1
    '2024_08_29_E6', #2
    '2024_08_30_E2', #3
    '2024_08_30_E5', #4
    '2024_09_03_E1', #5
    '2024_09_03_E4', #6
    '2024_09_03_E6' #7
]
all_notes = [Wind, Visual, Both]
all_notes_names = ['Wind','Visual', 'Both']
num_experiments = sum([len(condition) for condition in all_notes])