"""
This file holds all experiment names to be analyzed and used in angleDataframeCreation.py and plottingFunctions.py.
    
"""

# For each condition, create a list with each experiment in said condition and put the name in
# all_notes and all_notes_names (as a string) respectively.

wba_test = [
    '2025_03_18_E1', #0
    '2025_03_18_E2', #1
    '2025_03_18_E3', #2
    '2025_03_18_E4', #3
    '2025_03_18_E5', #4
    '2025_03_19_E1', #5
    '2025_03_19_E2', #6
    '2025_03_19_E3', #7
    '2025_03_19_E4', #8
    '2025_03_19_E5', #9
    '2025_03_19_E6' #10
]
 
all_notes = [wba_test]
all_notes_names = ['wba_test']
num_experiments = sum([len(condition) for condition in all_notes])