from pymongo import MongoClient


def get_client():
    CONNECTION_STRING = "mongodb://localhost:27017"

    return MongoClient(CONNECTION_STRING)
