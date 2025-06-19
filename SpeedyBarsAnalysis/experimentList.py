"""
This file holds all experiment names to be analyzed and used in angleDataframeCreation.py and plottingFunctions.py.
    
"""

# For each condition, create a list with each experiment in said condition and put the name in
# all_notes and all_notes_names (as a string) respectively.
Still = [
    '2024_05_23_E1', #0
    '2024_05_23_E2', #1
    '2024_05_23_E3', #2
    '2024_05_23_E4', #3
    '2024_05_23_E5', #4
    '2024_05_24_E1', #5
    '2024_05_24_E2', #6
    '2024_05_24_E3', #7
    '2024_05_24_E4', #8
    '2024_05_24_E5', #9
    '2024_05_28_E1', #10
    '2024_05_28_E2', #11
    '2024_05_28_E3', #12
    '2024_05_28_E4', #13
    '2024_05_28_E5', #14
    '2024_05_29_E1', #15
    '2024_05_29_E2', #16
    '2024_05_29_E3', #17
    '2024_05_29_E4', #18
    '2024_05_29_E5', #19
    '2024_06_13_E1', #20
    '2024_06_13_E2', #21
    '2024_06_14_E1', #22
    '2024_06_14_E2', #23
    '2024_06_14_E3', #24
    '2024_06_28_E1', #25
    '2024_06_28_E2', #26
    '2024_06_28_E3', #27
    '2024_06_28_E4', #28
    '2024_07_05_E1' #29
]

Cohesive = [
]

all_notes = [Still, Cohesive]
all_notes_names = ['Still','Cohesive']
num_experiments = sum([len(condition) for condition in all_notes])