from collections import namedtuple
from typing import List, Tuple
from utils import *
import sys

import tweepy
from decouple import config

# cnx = mysql.connector.connect(user='scott', password='password',
#                               host='127.0.0.1',
#                               database='employees')
from db import start_db

bearer_token = config('TWITTER_BEARER_TOKEN')
api_key = config('TWITTER_API_KEY')
api_secret = config('TWITTER_API_SECRET')
access_token = config('ACCESS_TOKEN')
access_token_secret = config('ACCESS_TOKEN_SECRET')
DB_HOST = config('DB_HOST')
DB_USER = config('DB_USERNAME')
DB_PASSWORD = config('DB_PASSWORD')
USERNAME = 'veritanonbugia'
USER_ID = 1457371398507220993

UserPinnedResponse = namedtuple("UserPinnedResponse", ("user_id", "username", "pinned_tweet"))


def select():
    return f"SELECT * FROM tweets WHERE used = False ORDER BY created_at ASC;"


Conn = start_db(DB_HOST, DB_USER, DB_PASSWORD)


def return_text_hashtags():
    cursor = Conn.cursor()
    cursor.execute(select())

    tweet_list = []
    for x in cursor:
        tweet_list.append(x)

    return tweet_list[0]


def mark_tweet_true(tweet_id):
    print(tweet_id)
    cursor = Conn.cursor()

    cursor.execute(f"UPDATE tweets SET used = TRUE WHERE id = {tweet_id}")
    Conn.commit()
    cursor.close()


class SimpleTwitter:

    def __init__(self):
        self.api = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_secret,
                                 access_token=access_token, access_token_secret=access_token_secret)

    def get_user_id_with_pinned_tweet(self, username='veritanonbugia') -> UserPinnedResponse:
        res: tweepy.Response = self.api.get_user(username=username, expansions='pinned_tweet_id')
        d = {'user_id': res.data.id, 'username': res.data.username, 'pinned_tweet': res.includes['tweets'][0]}

        return d

    # gets 10 most recent tweets
    def get_user_tweets(self, user_id=1457371398507220993):
        user_tweets = self.api.get_users_tweets(id=user_id, max_results=5)
        return user_tweets

    def tweet(self, raw_text):
        try:
            tup = SimpleTwitter.create_tweet(raw_text)
            final_text = tup[0]
            self.api.create_tweet(text=final_text)
            print('successfully created tweet')
            mark_tweet_true(raw_text[0])
        except Exception as E:
            print(E)

    def tweet_pinned(self, raw_text, pinned_id):
        try:
            self.api.create_tweet(text=raw_text, in_reply_to_tweet_id=pinned_id)
            print('successfully created tweet')

        except Exception as E:
            print(E)

    @staticmethod
    def create_tweet(raw_text: List) -> Tuple:
        t = None
        final_string = ''
        if raw_text[3] is None:
            final_string += raw_text[1]
        else:
            li = hashtags_as_list(raw_text[2])
            final_string += raw_text[1] + '\n'
            for tag in li:
                final_string += f"#{tag} "
            t = (final_string, raw_text[0])
        return t


#
client = SimpleTwitter()

# usr = client.get_user_id_with_pinned_tweet()
# print(usr.includes)

# twts = client.get_user_tweets()
# print(len(twts))
# print(twts)
# client.tweet(return_text_hashtags())
client.tweet_pinned('test', '1504832968883322909')

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print(tweet.text)
