from __future__ import print_function
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import os
from flask import Flask
from flask import request
from flask import make_response
app = Flask(__name__)


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
        result = best_product()
    elif req.get("queryResult").get("action") == "similar_product":
        result = similar_product()
    elif req.get("queryResult").get("action") == "friend_recommended":
        result = friend_recommended()
    
    my_result =  {

    "fulfillmentText": result,
     "source": result
    }
    return my_result
   

def best_product():
    return " function call for best product "

def friend_recommended():
    return "friend_recommended"

def similar_product():
    return "similar_product"


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')
