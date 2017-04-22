import nltk
import random
import pickle
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from nltk.classify import ClassifierI
from statistics import mode
from nltk.tokenize import word_tokenize
from trainer import trainClassifier

class sent(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        self.votes = []
        for self.i in self._classifiers:
            self.j = self.i.classify(features)
            self.votes.append(self.j)
        return mode(self.votes)

    def confidence(self, features):
        self.votes = []
        for self.i in self._classifiers:
            self.j = self.i.classify(features)
            self.votes.append(self.j)

        self.choice_votes = self.votes.count(mode(self.votes))
        self.conf = self.choice_votes / len(self.votes)
        return self.conf

    def featureFind(self,document,wf):
        self.words = word_tokenize(document)
        self.features = {}
        for self.i in wf:
            self.features[self.i] = (self.i in self.words)

        return self.features
    def ment(text):
        try:
            doc = pickle.load(open("pickle/doc.pickle", "rb"))
        except:
            print("Pickles missing!                                           ")
            print("Program will now constuct pickles, this may take some time.")
            trainClassifier().train()
            doc = pickle.load(open("pickle/doc.pickle", "rb"))
        wordFeat = pickle.load(open("pickle/wordFeat.pickle", "rb"))
        featSet = pickle.load(open("pickle/featSet.pickle", "rb"))
        ONB = pickle.load(open("pickle/ONB.pickle", "rb"))
        MNB = pickle.load(open("pickle/MNB.pickle", "rb"))
        BNB = pickle.load(open("pickle/BNB.pickle", "rb"))
        LR = pickle.load(open("pickle/LR.pickle", "rb"))
        LSVC = pickle.load(open("pickle/LSVC.pickle", "rb"))
        SGDC = pickle.load(open("pickle/SGDC.pickle", "rb"))

        vote = sent(ONB,MNB,BNB,LR,LSVC,SGDC)
        feats = sent().featureFind(text,wordFeat)
        out = (voted.confidence(feats))*100
        # out = str(out)+"%"
        return voted.classify(feats),out