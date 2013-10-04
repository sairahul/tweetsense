
import argparse
import json
import time

from pyelasticsearch import ElasticSearch

ES = ElasticSearch("http://localhost:9200")

TWEETS_SETTINGS = {
"settings" : { "index" : {  "analysis" : { "analyzer" : {  "lowercase_analyzer" : {  "type" : "custom",    "tokenizer" : "keyword", "filter":["lowercase"] } } } }},
    "mappings" : {
        "tweet" : {
            "_source": {
                "compress": true
             },
            "properties" : {
                "sentiment": {"type": "int"},
                "username": {"type": "string", "analyzer": "lowercase_analyzer"},
                "text": {"type": "string", "analyzer": "snowball"},
                "user_location": {"type": "string", "analyzer": "lowercase_analyzer"},
                "created": {"type": "date", "format": "dateOptionalTime"},
                "hashtags": {"type": "string", "analyzer": "lowercase_analyzer"},
                "user_mentions": {"type": "string", "analyzer": "lowercase_analyzer"},
                "country": {"type": "string", "analyzer": "lowercase_analyzer"},
                "profile_image_url": {"type": "string", "index": "no", "include_in_all": false}
            }
        }
    }
}


def create_index():
    resp = ES.create_index("tweets", settings=TWEETS_SETTINGS)
    print resp

def index(tweets):
        #resp = ES.index("wiki", "articles", {"title": title, "keywords": keywords, "aka": aka, "url": url, "inlinks": links}, id=rec["sk"])
        #print rec["doctitle"], links

    resp = ES.bulk_index("tweets", "tweet", records, id_field="gid")
    return resp

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-index', action='store_true')
    args = parser.parse_args()
    if args.create_index:
        create_index()


