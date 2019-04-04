import sys
import pandas as pd
import numpy as np
import scipy.sparse as sparse
from scipy.sparse.linalg import spsolve
import random

from sklearn.preprocessing import MinMaxScaler

import implicit 
from datetime import datetime, timedelta


def create_data(datapath,start_date,end_date):
    df=pd.read_csv(datapath)
    df=df.assign(date=pd.Series(datetime.fromtimestamp(a/1000).date() for a in df.timestamp))
    df=df.sort_values(by='date').reset_index(drop=True) # for some reasons RetailRocket did NOT sort data by date
    df=df[(df.date>=datetime.strptime(start_date,'%Y-%m-%d').date())&(df.date<=datetime.strptime(end_date,'%Y-%m-%d').date())]
    df=df[['visitorid','itemid','event']]
    return df

datapath= '../input/events.csv'
data=create_data(datapath,'2015-5-3','2015-5-18')
data['event']=data['event'].astype('category')
data['event']=data['event'].cat.codes
# The implicit library expects data as a item-user matrix so we
# create two matricies, one for fitting the model (item-user) 
# and one for recommendations (user-item)
sparse_item_user = sparse.csr_matrix((data['event'].astype(float), (data['itemid'], data['visitorid'])))
sparse_user_item = sparse.csr_matrix((data['event'].astype(float), (data['itemid'], data['visitorid'])))

# Initialize the als model and fit it using the sparse item-user matrix
model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=20)

# Calculate the confidence by multiplying it by our alpha value.
alpha_val = 15
data_conf = (sparse_item_user * alpha_val).astype('double')

# Fit the model
model.fit(data_conf)


#---------------------
# FIND SIMILAR ITEMS
#---------------------

# Find the 10 most similar to Jay-Z
item_id = 355908 #Jay-Z
n_similar = 10

# Get the user and item vectors from our trained model
user_vecs = model.user_factors
item_vecs = model.item_factors

# Calculate the vector norms
item_norms = np.sqrt((item_vecs * item_vecs).sum(axis=1))

# Calculate the similarity score, grab the top N items and
# create a list of item-score tuples of most similar artists

scores = item_vecs.dot(item_vecs[item_id]) / item_norms
scores=np.nan_to_num(scores)
top_idx = np.argpartition(scores, -n_similar)[-n_similar:]
similar = sorted(zip(top_idx, scores[top_idx] / item_norms[item_id]), key=lambda x: -x[1])

# Print the names of our most similar artists
'''

for item in similar:
    idx, score = item
    print(idx,score)

'''


#------------------------------
# CREATE USER RECOMMENDATIONS
#------------------------------


# Get the trained user and item vectors. We convert them to 
# csr matrices to work with our previous recommend function.
user_vecs = sparse.csr_matrix(model.user_factors)
item_vecs = sparse.csr_matrix(model.item_factors)

# Create recommendations for user with id 2025

user_id = 148114#257597
#number of users:


'''
list_scores_id=[]
for i in data['visitorid'].unique().tolist():
    print(i)
    list_scores_id.append([i,model.recommend(user_id, sparse_user_item,N=1)])
list_scores_id=[I[1] for I in list_scores_id]
list_scores_id.sort(key=lambda x: x[1],reverse=True)
'''    

def recommend(user_id,n=5):
    recommended = model.recommend(user_id, sparse_user_item,N=n)
    s='How about you try these products: '
    x=sorted(recommended,key=lambda x: x[1],reverse=True)
    recommended=[i[0] for i in recommended]
    return recommended
    for i in recommended:
        s+=str(i[0])+','
    return s[:-1]


def find_similar_user(user_id,n=5):
    s=model.similar_users(user_id, N=n)
    x=''
    s=[i[0] for i in s]
    return s
    for i in s:
        x+=str(i)+','
    return 'These are some of the similar users: '+ x[:-1]

def find_similar_items(item_id,n=5):
    similar = model.similar_items(item_id, n)
    x=''
    similar=[i[0] for i in similar]
    return similar
    for i in similar:
        x+=str(i)+','
    return 'These are some of the similar users: '+ x[:-1]





