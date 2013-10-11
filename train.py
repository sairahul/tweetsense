#!/usr/bin/python

import csv
import json
import sys
import re
import itertools

from numpy import loadtxt
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib
from sklearn.svm import SVC

URL_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def load_data(filename):
    fp = open(filename, 'rb')
    reader = csv.reader( fp, delimiter=',', quotechar='"' )
    tweets = []
    labels = []

    print('data loading ...')
    for i, row in enumerate(reader):
        tweet = row[-1]
        tweet = re.sub(URL_PAT, "HTTPURL", tweet) 

        tweets.append(tweet)
        labels.append(row[0])

    tweets, labels = shuffle(tweets, labels, random_state=1)

    tweets = tweets[:1000]
    labels = labels[:1000]

    return tweets, labels

# Help regarding the sentiment data
#http://help.sentiment140.com/for-students
"""
File Format
Data file format has 6 fields:
0 - the polarity of the tweet (0 = negative, 2 = neutral, 4 = positive)
1 - the id of the tweet (2087)
2 - the date of the tweet (Sat May 16 23:58:44 UTC 2009)
3 - the query (lyx). If there is no query, then this value is NO_QUERY.
4 - the user that tweeted (robotickilldozr)
5 - the text of the tweet (Lyx is cool)
"""
def train_nbclf(filename="training.1600000.processed.noemoticon.csv"):

    tweets, labels = load_data(filename)
    print('shuffling data ...')

    no_training_samples = int(len(tweets)*0.7)
    pipeline = Pipeline([
            ('vect', CountVectorizer(analyzer="word", ngram_range=(1,2), decode_error='ignore')),
            ('tfidf', TfidfTransformer(sublinear_tf=True, norm='l2')),
            #('chi2', SelectKBest(chi2, k=40000)),
            ('clf', MultinomialNB()),
        ])

    print("Training nb...")
    nb = pipeline.fit(tweets[:no_training_samples], labels[:no_training_samples])
    test_pred = nb.predict(tweets[no_training_samples:])

    print("Evaluating ...")
    mean = np.mean(test_pred == labels[no_training_samples:])
    print mean

    print('Dumping classifier ...')
    #joblib.dump(nb, 'nbclf.pkl')
    return nb

def train_rf(filename="training.1600000.processed.noemoticon.csv"):

    tweets, labels = load_data(filename)

    labels = [int(label) for label in labels]
    labels = np.array(labels)

    no_training_samples = int(len(tweets)*0.7)
    cv = CountVectorizer(analyzer="word", ngram_range=(1,2), decode_error='ignore')
    # have to pass all the tweets so that it will build the internal dicrionary correctly
    cv.fit(tweets)

    training = cv.transform(tweets[:no_training_samples]).tocsr()
    testing = cv.transform(tweets[no_training_samples:]).tocsr()

    training = training.toarray()
    testing = testing.toarray()

    clf = RandomForestClassifier(n_estimators=20)
    clf.fit(training, labels[:no_training_samples])

    print clf.score(testing, labels[no_training_samples:])

def grid_search_rf(filename="training.1600000.processed.noemoticon.csv"):
    tweets, labels = load_data(filename)

    labels = [int(label) for label in labels]
    labels = np.array(labels)

    no_training_samples = int(len(tweets)*0.7)
    cv = CountVectorizer(analyzer="word", ngram_range=(1,2), decode_error='ignore')
    cv.fit(tweets)

    training = cv.transform(tweets[:no_training_samples]).tocsr()
    testing = cv.transform(tweets[no_training_samples:]).tocsr()

    training = training.toarray()
    testing = testing.toarray()

    rf = RandomForestClassifier()
    parameters = {'n_estimators': np.arange(10, 40),
                  'max_depth': np.arange(1, 5)}
    clf = GridSearchCV(rf, parameters)
    clf.fit(training, labels[:no_training_samples])

    print(clf.best_params_)
    print(clf.best_score_)

if __name__=="__main__":
    #train_nbclf()
    #train_rf()
    print grid_search_rf()

