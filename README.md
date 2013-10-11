TweetSense
==========

This project is developed for demonstrating how to use various tools together.

Sentiment Analysis
==================

The data required for training can be downloaded from http://help.sentiment140.com/for-students

Used naive bayes for training our model. Check our train.py. 

Indexing the twitter data
=========================

Used elastic search for indexing the data. To create the elastic search index, 

```
python public_tweets.py --ceate-index
```

to start crawling the twitter data 

```
python public_tweets.py --crawl-public-tweets
````

UI
==

There is a rudimentary ui for searching the indexed data. It is based on flask and bootstrap. Used google visualization library and [http://dygraphs.com/] for graphs. Checkout ui/server.py

![ScreenShot](http://static.sairahul.com/tweetsense_1.png)
