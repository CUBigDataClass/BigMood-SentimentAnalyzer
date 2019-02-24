from flask import Flask
from flask import request
import getSentiment
import json
app = Flask(__name__)

@app.route('/sentimentjson',methods=['POST'])
def post():
    #if request.get_json()
    dataObj = request.get_json()
    sentEach = []
    sent = getSentiment.GetSentiment()
    for eachCountry in dataObj:
        #getSentiment returns a json object for the country
        sentEach.append(sent.getSentiment(eachCountry))
    retContentJson = json.dumps(sentEach)
    return retContentJson

app.run(host='0.0.0.0',port=5000)