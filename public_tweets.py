#!/usr/bin/env python

import argparse
import json
import time
import socket
from datetime import datetime

from twython import Twython
from twython import TwythonStreamer
from sklearn.externals import joblib
from pyelasticsearch import ElasticSearch

ES = ElasticSearch("http://localhost:9200")

APP_KEY = 'TkRvIk8ZT5VgUxEnDhrtQ'
APP_SECRET = 'VUoEVSSexAIEQTESpwT8JgwwsTgkXFDbgE1IJo4N5I'

OAUTH_TOKEN = '7779872-emavYipiuhSsyLb7IHyG8OrxZHtMfFs1vCXykv6uzJ'
OAUTH_TOKEN_SECRET = 'pgloCApQQ8ZP6ZH09qEqUaAcrOFVywU8LRgryljK6M'

CARBON_SERVER = '0.0.0.0'
CARBON_PORT = 2003
BATCH_SIZE = 100

TWEETS_SETTINGS = {
    "settings" : {
        "index" : {
            "analysis" : {
                "analyzer" : {
                    "lowercase_analyzer" : {
                        "type" : "custom",
                        "tokenizer" : "keyword",
                        "filter": ["lowercase"]
                    }
                }
            }
        }
    },
    "mappings" : {
        "tweet" : {
            "_source": {
                "compress": True
             },
            "properties" : {
                "sentiment": {"type": "integer"},
                "username": {"type": "string", "analyzer": "lowercase_analyzer"},
                "text": {"type": "string", "analyzer": "snowball"},
                "created": {"type": "date", "format": "dateOptionalTime"},
                "hashtags": {"type": "string", "analyzer": "lowercase_analyzer"},
                "user_mentions": {"type": "string", "analyzer": "lowercase_analyzer"},
                "country": {"type": "string", "analyzer": "lowercase_analyzer"},
                "profile_image_url": {"type": "string", "index": "no", "include_in_all": False}
            }
        }
    }
}

TWEETS = []
NBCLF = None

def update_graphite(message):
    print 'sending message: %s\n' % message
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    sock.close()

def load_nbclassifier():
    print('started loading nbclf ...')
    global NBCLF
    try:
        NBCLF = joblib.load("nbclf.pkl")
    except IOError:
        print('training nbclf ...')
        from train import train_nbclf
        NBCLF = train_nbclf()
    print('nbclf loaded')

load_nbclassifier()

def create_index():
    resp = ES.create_index("tweets", settings=TWEETS_SETTINGS)
    print resp

def format_tweets(tweets):
    _tweets = []
    for tweet in tweets:
        user_mentions = tweet['entities']['user_mentions']
        if user_mentions:
            user_mentions = [u.get('screen_name') for u in user_mentions]

        hashtags = tweet['entities']['hashtags']
        if hashtags:
            hashtags = [h.get('text') for h in hashtags]

        text = tweet['text']
        image = tweet['user']['profile_image_url']
        username = tweet['user']['screen_name']
        #created = tweet['created_at']
        created = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        #ptime = created.strftime("%Y/%m/%d %H:%M:%S %Z")
        ptime = created.strftime("%Y-%m-%dT%H:%M:%S")

        _id = tweet["id"]
        if tweet['place']:
            place = tweet['place']['country_code']
        else:
            place = ''

        sent = NBCLF.predict([text])
        _tweet = {"sentiment": sent[0],
                  "username": username,
                  "text": text,
                  "created": ptime,
                  "hashtags": hashtags or "",
                  "user_mentions": user_mentions or "",
                  "country": place,
                  "id": "%s"%(_id),
                  "profile_image_url": image}
        _tweets.append(_tweet)
    return _tweets

class ElasticSearchStreamer(TwythonStreamer):

    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, update_stats=True):
        super(ElasticSearchStreamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret)
        self.update_stats = update_stats

    def on_success(self, data):
        global TWEETS

        if not data.get('delete'):
            TWEETS.append(data)
        #else:
            #if self.update_stats:
            #    update_graphite("tweets.delete 1")

        if len(TWEETS)  == BATCH_SIZE:
            tweets = format_tweets(TWEETS)
            resp = ES.bulk_index("tweets", "tweet", tweets, id_field="id")
            print BATCH_SIZE
            #print resp
            TWEETS = []
            #if self.update_stats:
            #    update_graphite("tweets.indexed 100")

    def on_error(self, status_code, data):
        #if self.update_stats:
        #    update_graphite("tweets.errors 1")

        print status_code

def crawl_public_tweets(update_stats):
    stream = ElasticSearchStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, False)

    # Get random sample of all public statues
    # https://dev.twitter.com/docs/api/1.1/get/statuses/sample
    stream.statuses.sample()

if __name__=="__main__":
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--create-index', action='store_true')
    parser.add_argument('--crawl-public-tweets', action='store_true')
    parser.add_argument('--dont-update-stats', action='store_true', default=False)
    args = parser.parse_args()
    if args.create_index:
        create_index()
    elif args.crawl_public_tweets:
        crawl_public_tweets(not args.dont_update_stats)
    else:
        parser.print_help()

