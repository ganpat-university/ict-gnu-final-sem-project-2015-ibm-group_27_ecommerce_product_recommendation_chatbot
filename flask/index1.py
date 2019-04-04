from __future__ import print_function
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import os
from flask import Flask
from flask import request
from flask import make_response
#import ALS
from ALS_recommendation import find_similar_items,find_similar_user,recommend

app = Flask(__name__)
import pickle
import pandas as pd
lightfm_rec=pd.read_csv('lightfm_gen')
names_users=pd.read_csv('Names_list.csv')
names_items=pd.read_csv('product_list.csv')
items=pd.read_csv('../input/events.csv')['itemid'].unique().tolist()
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("queryResult").get("action") == "best_product":
        result = best_product(req)
    elif req.get("queryResult").get("action") == "similar_product":
        result = similar_product(req)
    elif req.get("queryResult").get("action") == "friend_recommended":
        result = friend_recommended(req)
    
    my_result =  {

    "fulfillmentText": result,
     "source": result
    }
    return my_result

def check_id(id_):
    #with open('user_id.pkl', 'rb') as fp:
        #users= pickle.load(fp)
    users=lightfm_rec['Unnamed: 0'].unique().tolist()
    
    ####check id uses user id.... into 
    print('>>>>>>>>>>>>>>>check',id_,type(id_))
    if(type(id_)=='str') :
        id_=eval(id_)
    if(id_ in users):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',id_, 'is verfiied')
        return True
    return False
def check_item_id(id_):
    #with open('user_id.pkl', 'rb') as fp:
        #users= pickle.load(fp)
    #users=lightfm_rec['Unnamed: 0'].unique().tolist()
    if(type(id_)=='str'):
        id_=eval(id_)
    ####check id uses user id.... into 
    print('>>>>>>>>>>>>>>>check',id_,type(id_))
    if(id_ in items):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',id_, 'is verfiied')
        return True
    return False
def get_url(msg):
    extra=[i for i in msg.split(' ') if len(i)>3]
    url_b='+'.join(extra[:2])
    url_a='https://www.amazon.in/s?k='
    url_c='&ref=nb_sb_noss_2'
    url=url_a+url_b+url_c
    return msg+url
    
    
def best_product_lightfm(id_):
    df=lightfm_rec
    e=df[df['Unnamed: 0']==id_]
    
    e=e.iloc[0,2:].tolist()
    msg=''
    print('>>>>>>>>>>>>>>>>>>list of products:',e,id_)
    e=[get_product_name(i) for i in e]
    e=[get_url(i) for i in e]
    for i in e:
        msg+='-->'+str(i)+'\n\n'
    
    return 'These are some of the best products recommended for you: '+ msg[:-1]+'\n'
def friend_recommended_prod(id_):
    '''
    df=lightfm_rec
    e=df[df['userid']==id_]
    e=e.iloc[0,1:].tolist()
    
    df=lightfm_rec
    e1=df[df['userid']==id_1]
    e1=e.iloc[0,1:].tolist()
    e=e[:3]+e1[:3]
    msg=''
    for i in e:
        msg+=str(i)+','
    
    return 'These are some of the similar users: '+ msg[:-1]
    '''    
    uid=find_similar_user(id_,2)
    #print('--------->>>>>>>>>>>>>',uid)
    df=lightfm_rec
    
    items_1=df[df['uid']==uid[0]].iloc[0,2:].tolist()
    items_2=df[df['uid']==uid[1]].iloc[0,2:].tolist()
    
    #print('---->>>>>>>>>',uid[0],uid[1])
    #items_1=recommend(uid[0],3)
    #items_2=recommend(uid[1],3)
    e=set(items_1[:3]+items_2[:3])
    e=[get_product_name(i) for i in e]
    msg=''
    e=[get_url(i) for i in e]
    for i in e:
        msg+='-->'+str(i)+'\n\n'
    
    return 'These are some of the similar users"s selected products: '+ msg[:-1]+'\n'
    
def get_product_name(id_):
    #print(id_,names_items.iloc[id_,:].values[1])
    id_=int(id_)
    #print('>>>>>>>>>>>>>>',id_)
    id_=items.index(id_)
    
    #print('>>>>>>>>>>>>',id_,names_items.iloc[id_,:].values[1])
    return names_items.iloc[id_,:].values[1]

def get_user_name(id):
    return names_users.iloc[id,:].values[1]
    
    
    
def best_product(req):
    #print('--->>>>>>>>>>>>>',req)#type(req.get("queryResult")[0]))
    try:id_=req.get("queryResult").get("outputContexts")[0].get('parameters').get('ID')
    except:
        id_=169612
        print('>>>>>>>>>>>>>>>default id for best product')
    #print('----->>>>>>',type(id_))
    check=check_id(id_)
    if(type(id)=='str'):
        
        id_=int(id_)
    if(check):
        msg=best_product_lightfm(id_)
    else:
        msg=best_product_lightfm(169612)
    
    return msg

def friend_recommended(req):
    try:id_=req.get("queryResult").get("outputContexts")[0].get('parameters').get('ID')
    
    except: id_=596477
    check=check_id(id_)
    if(check):
        msg=friend_recommended_prod(id_)
    else:
        msg=friend_recommended_prod(596477)
    
    
    return msg

def similar_product(req):
    
    #1985,2016,1908
    print(req)
    try:
        id_=req.get("queryResult").get("outputContexts")[0].get('parameters').get('pid')
        print(id_)
    except:id_=355908
    #check=check_id(id_)
    n=5
    check=check_item_id(id_)
    if(check):
            msg=find_similar_items(id_,n)
    else:
            msg=find_similar_items(123,n)
    st=''
    final=[]
    #print('--->>',msg)
    
    for i in msg:
        try:final.append(int(i))
        except: continue
    #print('--->>>>>',final,msg)
    msg=final
    
    #print(msg)
    msg=[get_product_name(i) for i in msg]
    msg=[get_url(i) for i in msg]
    #msg,url=get_url(msg)
    for i in msg:
        st+=str(i)+'\n\n'
    
    
    return 'Here are some similar Product: '+st[:-1]+'\n'




if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='127.0.0.1')


