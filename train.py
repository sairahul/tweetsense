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
from sklearn.utils import shuffle
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib
from sklearn.svm import SVC
from text.blob import TextBlob

URL_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

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

    print('shuffling data ...')
    tweets, labels = shuffle(tweets, labels, random_state=1)

    no_training_samples = int(len(tweets)*0.7)
    pipeline = Pipeline([
            ('vect', CountVectorizer(analyzer="word", ngram_range=(1,2), decode_error='ignore')),
            ('chi2', SelectKBest(chi2, k=40000)),
            ('clf', MultinomialNB()),
        ])

    print("Training nb...")
    nb = pipeline.fit(tweets[:no_training_samples], labels[:no_training_samples])
    test_pred = nb.predict(tweets[no_training_samples:])

    print("Evaluating ...")
    mean = np.mean(test_pred == labels[no_training_samples:])
    print mean

    print('Dumping classifier ...')
    joblib.dump(nb, 'nbclf.pkl')
    return nb

if __name__=="__main__":
    train_nbclf()

