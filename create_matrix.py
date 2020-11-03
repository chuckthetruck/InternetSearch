# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 14:36:42 2020

@author: CJ
"""

import ast
import numpy as np
import pandas as pd


def read_postings_list(doc):
    
    outlists = [[],[]]
    
    with open(doc) as file:
        lines = file.readlines()
        
    for line in lines:
        if line != '\n':
            spl = line.split(':\t')
            outlists[0].append(spl[0]) 
            outlists[1].append(ast.literal_eval(spl[1]))
        
    return outlists
    
    
postings = read_postings_list('stemmed_postings_list.txt')

with open('index.txt') as index:
    documents = (index.readlines())
    for i in range(len(documents)):
        documents[i] = ast.literal_eval(documents[i].strip())[1]
    size_of_index = len(documents)


documentmatrix = np.zeros((len(postings[0]),size_of_index))


for i in range(len(postings[1])):
    for tpl in postings[1][i]:
        documentmatrix[i][tpl[0]] += 1

postingsdf = pd.DataFrame(documentmatrix)
postingsdf['words'] = postings[0]
postingsdf.set_index(['words'],drop=True,inplace=True)

postingsdf.columns = documents
most_common = postingsdf.sum(axis=1)
most_common.sort_values(ascending=False,inplace=True)

frequency = postingsdf.astype(bool).sum(axis=1)

freq_most_common = frequency[most_common.index[0:20]]

freq_most_common.to_csv('stemmed_freq_most_common.csv')
postingsdf.to_csv('stemmed_freq_matrix.csv')
