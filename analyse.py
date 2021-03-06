import pymongo
import codecs
import json
import nltk
import threading
import random
from time import sleep
from pprint import pprint
from collections import Counter
from nltk.corpus import movie_reviews
from nltk.classify.scikitlearn import SklearnClassifier
from bson import Binary, Code
from bson.json_util import dumps

from display import display
from mongodb import mongo
from sentiment import sent

# The analyse class contain  methods that analyse the data in the database
class analyse:
    def __init__(self,db):
        self.db = db
        self.dis = display()

    def nltkDownload(self):
        try:
            nltk.data.find("tokenizers")
        except LookupError:
            #self.dis.spinner("Downloading NLTK Data")
            print("No NLTK data found, downloading now...")
            nltk.download("all")
            #self.dis.stop()
        

    # The searcher find tweets in the database with with the search term handed
    # to it with. It will return the tweets the term and number of times it 
    # apeares in the database in a dictionary.
    # It must be handed:
    #    *a search term as a string
    def counter(self,term):
        self.incremetor = 0
        self.tweetList = self.db.tweets.find({})
        for self.i in self.tweetList:
            if (term in self.i["tweet"]):
                #print(self.i["tweet"].encode("utf-8"))
                self.incremetor = self.incremetor + 1

        self.out = {
            "list":{self.tweetList},
            "term":{term},
            "counter": {self.incremetor}
        }

        return self.out

    # compare() compairs if people tweet about one thing or another more
    # it returns the winner.
    # It must be handed:
    #    *First term to compare as a string
    #    *Second term to compare as a string
    def compare(self,term1,term2):

        threading.Thread(target=self.dis.spinner, args=("Analysing Tweets ",)).start()

        self.search1 = analyse(self.db).counter(term1)
        self.search2 = analyse(self.db).counter(term2)
        
        self.dis.stop()

        print(term1,":",self.dis.joiner(self.search1["counter"]))
        print(term2, ":", self.dis.joiner(self.search2["counter"]))

        if(list(self.search2["counter"])[0] > list(self.search1["counter"])[0]):
            return term2
        return term1

    # Finds tweet in the database the have the search term handed to
    # it in.
    # It must be handed:
    #     *serach term
    def searcher(self,term):
        
        threading.Thread(target=self.dis.spinner, args=("Searching Database ",)).start()
        self.tweetList = []
        self.dbout = self.db.tweets.find({})
        for self.i in self.dbout:
            if term in self.i["tweet"].lower():
                self.tweetList.append(self.i)
            if "#"+term in self.i["tweet"]:
                self.tweetList.append(self.i)
        self.dis.stop()
        return self.tweetList


    # This method uses a word bank to find the sentiment of
    # tweets, it is a faster simpler way for finding sentiment.
    # It has been replaced by twitPollCompare() and the sent class
    # as main sentiment analyse.
    # It must be handed:
    #     *Search term
    def tweetMeaning(self,term):
        self.dbout = self.searcher(term)

        with open("data/words.json") as filedata:
            self.wordList = json.load(filedata)

        threading.Thread(target=self.dis.spinner, args=("Analysing Tweets ",)).start()
        self.tweetList = []
        for self.i in self.dbout:
            self.procounter = 0
            self.negcounter = 0
            for self.word in nltk.word_tokenize(self.i["tweet"]):
                #print("Analysing word: "+self.word)
                try:
                    if nltk.PorterStemmer().stem(self.word) in self.wordList["good"]:
                        #print("Found good world")
                        self.procounter = + 1
                    if nltk.PorterStemmer().stem(self.word) in self.wordList["bad"]:
                        #print("Found bad world")
                        self.negcounter = + 1
                    # if nltk.PorterStemmer().stem(self.word) in self.wordList["swear"]:
                    #     print("Found bad world")
                    #     self.negcounter = + 1
                    else:
                        self.neucounter = + 1
                except IndexError:
                    print("Ignoring tweet:",self.i["tweet"])

            self.view = "unknown"
            if self.procounter > self.negcounter:
                self.view = "pro"
            if self.negcounter > self.procounter:
                self.view = "neg"
            self.tweetDict = {
                "id": self.i["_id"],
                "tweet": self.i["tweet"],
                "procount": self.procounter,
                "negcount": self.negcounter,
                # "view":"pro" if self.procounter > self.negcounter else "neg"
                "view": self.view
            }
            self.tweetList.append(self.tweetDict)
        self.dis.stop()
        return self.tweetList
        
    # This method gets the poll data from the JSON file it is 
    # stored in, ii then adds them up to get a total.
    def getPollData(self):
        with open("data/polls.json") as filedata:
            self.data = json.load(filedata)

        self.remainTot = 0
        self.leaveTot = 0
        self.unsureTot = 0

        for self.i in self.data["polls"]:
            self.remainTot = self.remainTot + self.i["remain"]
            self.leaveTot = self.leaveTot + self.i["leave"]
            self.unsureTot = self.unsureTot + self.i["unsure"]

        self.pollDict = {
            "remain":self.remainTot,
            "leave":self.leaveTot,
            "unsure":self.unsureTot,
            "remainPer": (self.remainTot / (self.remainTot + self.leaveTot + self.unsureTot)) * 100,
            "leavePer": (self.leaveTot / (self.remainTot + self.leaveTot + self.unsureTot)) * 100
        }
        return self.pollDict


    # This finds the most common hashtags used in the database
    def getHashtags(self):
        self.twitRes = analyse(self.db).tweetMeaning("brexit")

        threading.Thread(target=self.dis.spinner, args=("Counting Hashtags ",)).start()
        self.f = open("tweets.txt", "w")

        self.hashList = []

        for self. i in self.twitRes:
            for self.j in self.i["tweet"].split():
                if self.j[0] == "#":
                    self.hashList.append(self.j.lower())

        for self.i in Counter(self.hashList).most_common(100):
            try:
                self.f.write(self.i[0]+"\n")
            except UnicodeEncodeError:
                print("UnicodeEncodeError")

        self.dis.stop()

    # this method hands the tweets to sentiment analyse then copares the
    # results with the polls to find the difference. It outputs the 
    # results to the user.
    def twitPollCompare(self):
        self.pollRes = analyse(self.db).getPollData()
        self.twitRes = analyse(self.db).searcher("brexit")

        threading.Thread(target=self.dis.spinner, args=("Grouping by Hashtag ",)).start()

        self.remainList = []
        self.leaveList = []
        self.unknList = []
        self.nullList = []

        self.remainHash = ["#remain", "#strongerin", "#voteremain", "#bremain","#brexitthemovie","#remainineu","#scotland","#votein","#in","#labourinforbritain","#eureflondon","#indyref"]
        self.leaveHash = ["#voteleave", "#leaveeu", "#takecontrol", "#leave", "#voteout", "#betteroffout","#out","#takebackcontrol"]

        for self.i in self.twitRes:
            if any(self.term in self.i["tweet"].lower() for self.term in self.remainHash):
                self.remainList.append(self.i)
            elif any(self.term in self.i["tweet"].lower() for self.term in self.leaveHash):
                self.leaveList.append(self.i)
            else:
                self.unknList.append(self.i)

        self.dis.stop()

        # threading.Thread(target=self.dis.spinner, args=("Checking remain tweet sentiment",)).start()

        for self.i in self.remainList:
            print("                                               ",end="\r")
            print("Remain list items remaing:",len(self.remainList),end="\r")
            self.sentiment = sent.ment(self.i["tweet"])
            if self.sentiment[1] > 50:
                if self.sentiment[0] == "neg":
                    self.leaveList.append(self.i)
                    self.remainList.remove(self.i)
            else:
                self.nullList.append(self.i)
                self.remainList.remove(self.i)      
            # break   
        print("Complete...                                                  ")
        # self.dis.stop()

        # threading.Thread(target=self.dis.spinner, args=("Checking leave tweet sentiment",)).start()  
     

        for self.i in self.leaveList:
            print("Leave list items remaing:",len(self.leaveList),end="\r")
            self.sentiment = sent.ment(self.i["tweet"])
            if self.sentiment[1] > 50:
                if self.sentiment[0] == "neg":
                    self.remainList.append(self.i)
                    self.leaveList.remove(self.i)
            else:
                self.unknList.append(self.i)
                self.leaveList.remove(self.i)
            # break

        print("Complete...                                                  ")
        # self.dis.stop()

        # threading.Thread(target=self.dis.spinner, args=("Checking unknown tweet sentiment",)).start()

        for self.i in self.unknList:
            print("Unknown list items remaing:",len(self.unknList),end="\r")
            self.sentiment = sent.ment(self.i["tweet"])
            if self.sentiment[1] > 50:
                if self.sentiment[0] == "pos":
                    self.leaveList.append(self.i)
                    self.unknList.remove(self.i)
                else:
                    self.remainList.append(self.i)
                    self.unknList.remove(self.i)
            else:
                self.nullList.append(self.i)
                self.unknList.remove(self.i)
            # break

        print("Complete...                                                  ")
        # self.dis.stop()

        self.procount = len(self.remainList)
        self.negcount = len(self.leaveList)
        self.nullcount = len(self.nullList)
        self.unkncount = len(self.unknList)
        
        self.twitRemainPer = (self.procount / (self.procount + self.negcount)) * 100
        self.twitLeavePer = 100 - self.twitRemainPer

        self.data = {
            "remainCount":self.procount,
            "leaveCount":self.negcount,
            "unknCount":self.unkncount,
            "nullcount":self.nullcount
            #"remainList":self.remainList[1],
            #"leaveList":self.leaveList[1]
            #"nullList":self.nullList[1]
        }

        print(self.data)
        with open("data/results.json","w") as self.file:
            json.dump(self.data,self.file)

        self.file.close()

        print ("Poll Results:",
        "\n    Remain:", round(self.pollRes["remainPer"],1), "% ({})".format(self.pollRes["remain"]),
        "\n    Leave:",round(self.pollRes["leavePer"],1),"% ({})".format(self.pollRes["leave"]),
        "\nTwitter Results:",
        "\n    Remain:",round(self.twitRemainPer,1),"% ({})".format(self.procount),
        "\n    Leave:",round(self.twitLeavePer,1),"% ({})".format(self.negcount),
        "\n    Null:",self.nullcount,
        )

    # This method gets the last analyse data from the JSON file
    # it is stored in, then it outputs it to the user
    def outOldData(self):
        with open("data/results.json","r") as self.file:
            self.data = json.load(self.file)

        self.procount = self.data["remainCount"]
        self.negcount = self.data["leaveCount"]
        self.nullcount = self.data["nullcount"]

        self.pollRes = analyse(self.db).getPollData()

        self.twitRemainPer = (self.procount / (self.procount + self.negcount)) * 100
        self.twitLeavePer = 100 - self.twitRemainPer
        
        print ("Poll Results:",
        "\n    Remain:", round(self.pollRes["remainPer"],1), "% ({})".format(self.pollRes["remain"]),
        "\n    Leave:",round(self.pollRes["leavePer"],1),"% ({})".format(self.pollRes["leave"]),
        "\nTwitter Results:",
        "\n    Remain:",round(self.twitRemainPer,1),"% ({})".format(self.procount),
        "\n    Leave:",round(self.twitLeavePer,1),"% ({})".format(self.negcount),
        "\n    Null:",self.nullcount,
        )

    # Test method for testing things.
    def test(self):
        # self.out = analyse(self.db).searcher("")
        # print (len(self.out))
        self.tweetList = []
        self.dbout = self.db.tweets.find({})
        for self.i in self.dbout:
            self.tweetList.append(self.i)
        
        
        self.counter = 0
        for self.i in self.tweetList:
            if "brexit" not in self.i["tweet"].lower():
                print(self.i["tweet"],"\n\n")
                self.counter = self.counter + 1
        print(len(self.tweetList))
        print(self.counter)