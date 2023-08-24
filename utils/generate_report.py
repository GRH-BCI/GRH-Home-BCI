import os
import datetime
import numpy as np
import pandas as pd

''' 
    function that handles generating report.csv files based on the targets and activation timings.
    does not generate the csv if there are no activations
    target: created by manually pressing a switch used by the third-party via the AT hub 
    activation: created by the user and emotiv headset 
    success_threshold: minimum allowed delay between target and closest activation 
'''
def generate_report(success_threshold: int, activations, targets):
    print(success_threshold)
    print(activations)
    print(targets)
    refined_tgt = [targets[i][1] for i in range(len(targets))]
    path = './data_sets'
    '''
        check whether path already exists. if not create the path folder and save report.csv in the path 
    '''
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        print("Folder %s already exists" % path)
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_name = 'Report_' + str(current_datetime) + '.csv'
    next_activation = []
    activation_delay = []
    if len(activations) != 0:
        for tgt in refined_tgt:
            temp = float('inf')
            res = float('inf')
            for act in activations:
                if 0 < float(act - tgt) < temp:
                    temp = act - tgt
                    res = act
            next_activation.append(res)
            activation_delay.append(res - tgt)
    print(next_activation, activation_delay)
    success = len([i for i in activation_delay if i <= success_threshold])

    success_rate = [100 * float(success / len(activations))] if not len(activations) == 0 else 0

    out = dict(target=np.array(refined_tgt), activation=np.array(activations),
               closest_activation=np.array(next_activation),
               activation_lag=np.array(activation_delay), success_threshold=np.array([success_threshold]),
               success_rate=np.array(success_rate))

    '''
        check for zero length of activations. generate warning if no activations before generating a report  
    '''
    if len(activations) != 0:
        DF = pd.DataFrame.from_dict(out, orient='index')
        DF = DF.T
        print(DF.info)
        DF.to_csv('./data_sets/' + file_name)
    else:
        print("no activations ")
