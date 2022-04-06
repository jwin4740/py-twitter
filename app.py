import sys
from collections import namedtuple
from typing import List, Tuple

from tweepy import HTTPException

from utils import *
from datetime import datetime
import time

import tweepy
from decouple import config
import requests
import json

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
VERITA_USERNAME = 'veritanonbugia'
VERITA_USER_ID = 1457371398507220993
VERITA_PINNED_TWEET_ID = '1504832968883322909'

MAVX_USERNAME = 'ErickMavx'
MAVX_USER_ID = 1507745273321242635
MAVX_PINNED_TWEET_ID = '1507747124544512010'
COUNTER_401 = 0
COUNTER_403 = 0
COUNTER_429 = 0

UserPinnedResponse = namedtuple("UserPinnedResponse", ("user_id", "username", "pinned_tweet"))

MAVX_TEXT = f"Even as little as a $2 donation can help fund our clinical trial on the effect of Covid vaccines on human health.\n\nNo government agency will help with this study. We need YOUR help!!! Please donate and retweet.\n\nhttps://givesendgo.com/TheMavxerickStudy"
BULLY_TEXT = f"Anyone who still wears a mask should be bullied, this is beyond ridiculous."
BIO_WEAPON = f"We need to stop using the term \"vaccine\", this is a lipid nano particle encapsulated bioweapon"
FOURTH_DOSE = f"Fourth dose of the bioweapon approved by FDA with ZERO data and regulatory insight"
REMDESIVIR = f"Interesting, the Wuhan lab also developed REMDESIVIR; but definitely no connection to Gain-of-Fauci research"


def select():
    return f"SELECT * FROM tweets WHERE used = False ORDER BY created_at ASC;"


# Conn = start_db(DB_HOST, DB_USER, DB_PASSWORD)


# def return_text_hashtags():
#     cursor = Conn.cursor()
#     cursor.execute(select())
#
#     tweet_list = []
#     for x in cursor:
#         tweet_list.append(x)
#
#     return tweet_list[0]


# def mark_tweet_true(tweet_id):
#     print(tweet_id)
#     cursor = Conn.cursor()
#
#     cursor.execute(f"UPDATE tweets SET used = TRUE WHERE id = {tweet_id}")
#     Conn.commit()
#     cursor.close()


class SimpleTwitter:

    def __init__(self):
        self.api = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_secret,
                                 access_token=access_token, access_token_secret=access_token_secret)

    def get_user_id_with_pinned_tweet(self, username='veritanonbugia'):
        d = ''
        try:
            res: tweepy.Response = self.api.get_user(username=username, expansions='pinned_tweet_id')
            d = {'user_id': res.data.id, 'username': res.data.username, 'pinned_tweet': res.includes['tweets'][0]}
            print(d['pinned_tweet']['data']['id'])
        except Exception as E:
            with open('verita.log', 'a') as f:

                f.write(f"{datetime.now()} error {E} fetching pinned tweet {username}\n")

        return d

    # gets 10 most recent tweets
    def get_user_tweets(self, user_id=VERITA_USER_ID):
        user_tweets = self.api.get_users_tweets(id=user_id, max_results=5)
        return user_tweets

    def tweet(self, raw_text):
        try:
            tup = SimpleTwitter.create_tweet(raw_text)
            final_text = tup[0]
            self.api.create_tweet(text=final_text)
            print('successfully created tweet')
            # mark_tweet_true(raw_text[0])
        except Exception as E:
            print(E)

    def tweet_reply(self, t_id, msg_text):

        try:
            self.api.create_tweet(text=msg_text, in_reply_to_tweet_id=t_id)

        except HTTPException as E:
            self.handle_exception(E)

        print('successful reply to tweet')

    def get_followers(self, user_id=VERITA_USER_ID):
        next_token = True
        pagination_token = None
        followers_list = []
        while next_token is True:
            followers = self.api.get_users_followers(user_id, pagination_token=pagination_token)
            flw_list = followers.data
            for follower in flw_list:
                followers_list.append(follower)
            try:
                pagination_token = followers.meta['next_token']

            except Exception as E:
                next_token = False
                print(E)
        return followers_list

    def tweet_pinned(self, raw_text, pinned_id, user_name):
        try:
            self.api.create_tweet(text=raw_text, in_reply_to_tweet_id=pinned_id)
            print('successfully created tweet')
            with open('verita.log', 'a') as f:
                text_strip = MAVX_TEXT.replace('\n', ' ')
                f.write(f"{datetime.now()} POSTED {text_strip} TO {user_name}\n")

        except Exception as E:
            with open('verita.log', 'a') as f:
                f.write(f"{datetime.now()} {E} POSTING TO {user_name}\n")

    def search_tweets_by_keyword(self, keyword):

        next_token = True
        pagination_token = None
        tweet_list = []
        max_tweets = 1000

        while next_token is True:
            time.sleep(0.5)
            res = self.api.search_recent_tweets(keyword, next_token=pagination_token)
            print('successfully fetched batch')

            tw_list = res.data
            for follower in tw_list:
                tweet_list.append(follower)
            try:
                pagination_token = res.meta['next_token']
                if len(tweet_list) > max_tweets:
                    next_token = False
            except Exception as E:
                next_token = False
                print(E)
        return tweet_list

    def handle_exception(self, exception: HTTPException):
        if exception.response.status_code == 403:
            global COUNTER_403
            COUNTER_403 += 1
            with open('verita.log', 'a') as f:
                f.write(f"{datetime.now()} error {exception}\n")

        if exception.response.status_code == 401:
            global COUNTER_401
            COUNTER_401 += 1

            with open('verita.log', 'a') as f:
                f.write(f"{datetime.now()} error {exception}\n")

        if exception.response.status_code == 429:
            with open('verita.log', 'a') as f:
                f.write(f"{datetime.now()} error {exception} exiting...\n")
            sys.exit(1)

    def test_req(self):
        try:
            self.api.create_tweet(text='blobbb', in_reply_to_tweet_id=43434)
        except HTTPException as E:
            self.handle_exception(E)

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


# usr = client.get_user_id_with_pinned_tweet('SuePear85834959')

# twts = client.get_user_tweets(MAVX_USER_ID)
# print(len(twts))
# print(twts)


# client.tweet_pinned(MAVX_TEXT, VERITA_PINNED_TWEET_ID)

# client.get_user_id_with_pinned_tweet('sbhank')
# sbhank pinned tweet '1241409878448467970'

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print(tweet.text)
def execute():
    fl_list = client.get_followers()
    print(fl_list)
    pinned_tweet_id = ''
    for follower in fl_list:
        follow_data = {
            'username': follower.username,
            'id': follower.id
        }
        print(follow_data)
        try:
            time.sleep(3)
            res = client.get_user_id_with_pinned_tweet(follow_data['username'])
            if res == '':
                continue
            pinned_tweet_id = res['pinned_tweet']['data']['id']
        except Exception as E:
            with open('verita.log', 'a') as f:
                f.write(f"{datetime.now()} {E} POSTING TO {follow_data['username']}\n")
        try:
            time.sleep(3)

            client.tweet_pinned(BULLY_TEXT, pinned_tweet_id, follow_data['username'])
        except Exception as E:
            with open('verita.log', 'a') as f:
                f.write(f"{datetime.now()} {E} POSTING TO {follow_data['username']}\n")


def get_tweets_by_keyword(kw: str, txt: str):
    tweets = client.search_tweets_by_keyword(kw)
    skipper = 0
    counter = 0
    for tweet in tweets:
        try:
            c_id = tweet['data']['id']
            if counter >= skipper:
                if counter < 25:
                    time.sleep(3)
                else:
                    time.sleep(45)
                # TODO: If 403 response too many times, exit program
                if COUNTER_401 < 3 or COUNTER_403 < 3:
                    actual_text = txt + " " + str(counter)
                    client.tweet_reply(c_id, actual_text)
                else:
                    with open('verita.log', 'a') as f:
                        f.write(f"{datetime.now()} EXITED because of 401 or 403 excess\n")
                    sys.exit(1)
                with open('verita.log', 'a') as f:
                    tweet_strip = tweet.text.replace('\n', '')
                    f.write(f"{datetime.now()} POSTED MESSAGE TO {tweet_strip} WITH KEYWORD {kw}\n")
            counter += 1
        except Exception as E:

            print(E)


get_tweets_by_keyword('COVID19', REMDESIVIR)
