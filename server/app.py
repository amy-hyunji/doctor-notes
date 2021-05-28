from flask import Flask, abort, jsonify, request, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@cross_origin

@app.route('/')
def home():
    return "Welcome to server!"

@app.route('/tryout', methods=["GET", "POST"])
def tryout():
    if request.method == 'POST':
        sentence_from_req = request.json["sentence"]
        print(sentence_from_req)
    
    return "successfully accessed method!"


@app.route('/second/tryout', methods=["GET", "POST"])
def tryoutsecond():
    return "tryout second succesful!"
'''
@app.route('/api', methods=['GET'])
def api():
    return {
        'userId': 1,
        'title': 'Flask React Application',
        'completed': False
    }

'''
app.run(debug=True)