# This file connects to the MongoDB using the pymongo library.

import pymongo
import json
from pymongo import MongoClient

class mongo:

    # function that is called to connect to the MongoDB, it returns an
    # an operator to send commands to the DB with
    def conn(self):
        #gets the mongo credentials from a json file
        with open("mongoCredentials.json") as dataFile:
            cred = json.load(dataFile)

        self.client = MongoClient(cred["mongoURL"])  # sets the client (change the url mongoCredentials.json)
        self.db = self.client.tweetsDB #creates an operator for accessing the DB 
        return self.db #returns the operator
