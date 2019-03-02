from flask import Flask
import pymongo
from pymongo import MongoClient
import pprint
app = Flask(__name__)

@app.route("/")
def hello():
    client = MongoClient()
    db = client["stacshack"]
    users = db.users
    return pprint.pformat(users.find_one())