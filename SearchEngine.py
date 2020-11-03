import ast
import numpy as np
import pandas as pd
import copy
from nltk.stem import PorterStemmer

def similarity(index,q_table,d_table):
    #making the document vectors ltc   
    d_v = d_table.copy()
 
    # Logrithmic term frequency
    with np.errstate(divide='ignore'):
        d_v = (1+(np.log(d_v)))
    d_v = d_v.replace(-np.inf,0)
    
    # making idf
    d_v['idf'] = -1
    for i in d_v.index:
        cur_row = d_table.loc[i]
        d_v.loc[i,'idf'] = np.log((len(d_table.columns)/len(cur_row[cur_row>0])))
        
    d_v.update(d_v[d_table.columns].mul(d_v.idf,0))
    
    # Cosine Normalizination of document vector
    for c in d_table.columns:
        d_v[c]=d_v[c].mul(1/np.sqrt(np.sum(np.square(d_table[c]))),0)  
    
    # making the query vector lnc
    q_v = q_table.copy()
    q_v = (1+(np.log(q_v)))
    q_v = q_v.replace(-np.inf,0)
    
    # cosine normalization of q vector
    cosine = 1/np.sqrt(np.sum(np.square(q_v.iloc[:,0])))    
    q_v = q_v.multiply(cosine)
    
    # remove the words not in the query from the document vectors
    # equivalent to multiplying them by zero
    d_v = d_v.loc[q_v.index,:]
    
    # calculate the similarity scores
    for c in list(d_table.columns):
        d_v[c] = d_v[c].mul(q_v[0],0)
        d_v.loc['sim_score',c] = np.sum(d_v[c])
    
    # add 0.1 to every instance that a query word appears in the title
    for q in q_v.index:
        for d in index:
            if q.lower() in d[2].lower():
                d_v.loc['sim_score',d[1]] += 0.1

    return d_v.loc['sim_score',d_table.columns]


def search(query,index,thesuarus,stemmer):
    # create a list of the query terms
    search_terms = query.split()
    tf_query = {}
    
    i=0
    while i < len(search_terms):
        term = copy.deepcopy(search_terms[i])
        
        # add synonyms of words to the query
        if term in thesuarus.keys():
            if thesuarus[term] and thesuarus[term][0] not in search_terms:
                search_terms.extend(thesuarus[term])
        
        #stem the query terms        
        search_terms[i] = stemmer.stem(search_terms[i])
        
        # add the query terms to a dictionary and count the number of instances 
        # of each term
        if search_terms[i] in tf_query.keys():
            tf_query[search_terms[i]] +=1
        
        else:
            tf_query[search_terms[i]] =1
            
        i+=1
    
    # create query and document vectors    
    tf_query = pd.DataFrame.from_dict(tf_query,orient='index')    
    tf_docs = pd.read_csv('stemmed_freq_matrix.csv')     

    # remove words not found in the dictionary from the query
    tf_query = tf_query.loc[tf_query.index.isin(tf_docs['words'])]    
    tf_docs.set_index('words',drop=True,inplace=True)     
    
    sim = similarity(index,tf_query,tf_docs)
    
    return sim
    

def read_postings(loc):
    with open(loc) as file:
        lines = file.readlines()
        
    new_lines = {}
    
    for line in lines:
        temp = line.split(':\t')
        
        new_lines[temp[0]] = ast.literal_eval(temp[1])
        
    return new_lines


# read the posings list opreviously created
postings = read_postings('stemmed_postings_list.txt')

# thesaurus of select words
thesuarus = {'beautiful':['fancy','nice'],'chapter':['chpt'],'chpt':['chapter'],
             'responsible':['owner','accountable'],
             'freemanmoore':['freeman','moore'],'dept':['department'],
             'photo':['photograph','image','picture'],
             'brown':['tan','beige','auburn'],'tues':['Tuesday'],
             'sole':['owner','single','shoe','boot'],
             'homework':['hmwk','home','work'],'novel':['book','unique'],
             'computer':['cse'],'story':['novel'],
             'hocuspocus':['magic','abracadabra'],'thisworks':['this','works']
             }

# read the index
with open('index.txt') as file:
    index = file.readlines()
    
# transform index from list of strings to list of Tuples
for i in range(len(index)):
    index[i] = ast.literal_eval(index[i])

# main loop
while True:
    query = input('Please type a search. Input "stop" to exit.\n')
    stemmer = PorterStemmer()
    if query.lower() == 'stop':
        break
    
    sim = search(query,index,thesuarus,stemmer)
    
    sim.sort_values(ascending=False,inplace=True)
    
    top5 = sim.iloc[0:5]
    
    for i in top5.index:
        for j in index:
            if i == j[1]:
                print('sim score: {0}\nUrl: {1}\nTitle: {2}'.format(sim[i],j[0],j[2]))
                print('Sample: ')
                
                docname='doc_repo/'+j[1]
                with open(docname) as file:
                    text = file.read()                    
                    first20 = text.split()
                    
                    if len(first20) < 20:   
                        first20 = ' '.join(first20)
                        
                    else:
                        first20 = ' '.join(first20[:20])
                        
                    print(first20)    
                    print()
                        
                break
                
    
    






