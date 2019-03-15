# /index.py

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_movie_detail', methods=['POST'])
def get_product_detail():
    data = request.get_json(silent=True)
    product = data['queryResult']['parameters']['product']
    api_key = os.getenv('OMDB_API_KEY')

    product_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(product, api_key)).content
    product_detail = json.loads(product_detail)
    response =  """
        Brand : {0}
        Detail: {1}
        Price: {2}
        Quantity: {3}
    """.format(product_detail['Brand'], product_detail['Detail'], product_detail['Price'], product_detail['Quantity'])

    reply = {
        "fulfillmentText": response,
    }

    return jsonify(reply)

def detect_intent_texts(project_id, session_id, text, language_code):
    
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result.fulfillment_text


@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }

    return jsonify(response_text)



# run Flask app
if __name__ == "__main__":
    app.run()
    
    
