import asyncio
from jsonschema import validate
from flask import Flask, request, jsonify
import pymongo
from bson import ObjectId
from pymongo import MongoClient
import pprint
import json
from bson.json_util import dumps
app = Flask(__name__)

client = MongoClient()
db = client["stacshack"]

matches = []

def valid_user(user):
    schema = {
        "type": "object",
        "properties": {
            "username": { "type": "string" },
            "answers": { "type": "array" },
        },
    }

    return validate(instance=user, schema=schema)

def find_user(id): return db.users.find_one({'_id': id})

@app.route("/", methods=['GET'])
def hello():
    users = db.users
    if request.method == 'GET':
        print("Here")
    return pprint.pformat(users.find_one())

@app.route("/questions.json", methods=['GET'])
def questions():
    questions = db.questions.find({}, {'_id': False})
    questions_json = jsonify(list(questions))
    return questions_json

@app.route("/user", methods=['POST'])
def user():
    users = db.users
    user = request.get_json()
    user = users.insert_one(user)
    return str(user.inserted_id)

def make_match(id_str):
    userID = ObjectId(id_str)
    user = find_user(userID)
    users = list(db.users.find({'_id': {'$ne': userID}}))
    if len(users) == 0: return ""
    answers = user["questionAnswers"]
    num_match = {}
    print("users: "+ str(users))
    for other_user in users:
        num_match[str(other_user['_id'])] = sum([1 if answers[i] == other_user["questionAnswers"][i] else 0 for i in range(len(other_user["questionAnswers"]))])

    num_match = sorted(num_match.items(), key=lambda kv: kv[1], reverse=True)
    pprint.pprint(num_match)
    for other_user, num in num_match:
        if num >= 3:
            matched_user = db.users.find_one(ObjectId(other_user))
            print(matched_user)
            return str(matched_user['_id'])
    
        
    return ""

@app.route("/find_match", methods=['POST'])
def find_match():
    id_str = request.get_json()['id']
    global matches
    match = [pair for pair in matches if id_str in pair]
    if len(match) != 0:
        print("a match?")
        match = match[0]
        other = match[0] if match[0] != id_str else match[1]
        otherID = ObjectId(other)
        matches = [pair for pair in matches if pair[0] != id_str and pair[1] != id_str]
        return find_user(otherID)
    else:
        print("lonley")
        other = make_match(id_str)
        if other != "":
            print("found someone")
            matches.append((id_str, other))
            return find_user(ObjectId(other))
        else:
            print("forever alone")
            return dumps({})


    