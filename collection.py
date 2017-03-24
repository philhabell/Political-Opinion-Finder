import tweepy #Twitter API library
import codecs #encoding library for encodeding tweets in utf-8
import pymongo #mongo library
import time
import urllib
import json
import got3 #library that allows search for legacy tweets. Written by Jefferson Henrique (https://github.com/Jefferson-Henrique/GetOldTweets-python). Nothing in the got3 (GetOldTweets3) folder is written by me and I do not claim to have done!
from pymongo import MongoClient #gets the mongo client method


from authGet import twitterAPI
from mongodb import mongo
from locGet import geo
from analyse import analyse

class collection:
    def __init__(self, api, db):
        self.api = api
        self.db = db

    #gets tweets from hashtag "#brexit" and puts them in the mongo database
    def getTweets(self, hashtag):

        self.tweetCriteria = got3.manager.TweetCriteria().setQuerySearch(hashtag).setSince("2016-06-12").setUntil("2016-06-13").setMaxTweets(20000)
        self.brexitTweets = got3.manager.TweetManager.getTweets(self.tweetCriteria)

        # brexitTweets =
        # tweepy.Cursor(api.search,q="#brexit",show_user=True,locale=True,wait_on_rate_limit=True).items()

        #loops through the list of tweets
        for self.tweets in self.brexitTweets:

            self.out = self.tweets.text
            self.name = self.tweets.username
            self.uid = self.tweets.author_id
            self.tweetid = self.tweets.id
            self.date = self.tweets.date
            self.geo = geo().locFind(self.name)
            self.followers = []
            self.friends = []
            self.tmp = 0

            #gets the users followers id and puts them in a list
            #for self.followersID in tweepy.Cursor(self.api.followers_ids, screen_name=self.name, wait_on_rate_limit=True, wait_on_rate_limit_notify=True).items(100):
                #print ("Adding to followers list: ",users)
                #self.followers.append(self.followersID)

            #gets the users following and puts them in the list
            #for self.followingID in tweepy.Cursor(self.api.friends_ids, screen_name=self.name, wait_on_rate_limit=True, wait_on_rate_limit_notify=True).items(100):
                #print ("Adding to friends list: ",users.screen_name)
                #self.friends.append(self.followingID)

            #shows what is being added to the database
            print("\n\nAdded:",  
                "\n    User ID:", self.uid, 
                "\n    Tweet ID:", self.tweetid, 
                "\n    Username:", self.name.encode("utf-8"),
                "\n    Date:", self.date, 
                "\n    Location:", self.geo.encode("utf-8"),
                "\n    Tweets:", self.out.encode("utf-8"),
                "\n    Followers:", self.followers, 
                "\n    Following:", self.friends,)  # shows tweets being added to the DB

            #adds the data to the database
            self.results = self.db.tweets.insert_one(
                {
                    "userID": self.uid,
                    "tweetID": self.tweetid,
                    "username": self.name,
                    "date": self.date,
                    "location:": self.geo,
                    "tweet": self.out,
                    "followers": self.followers,
                    "friends": self.friends
                }
            )
