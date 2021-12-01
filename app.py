from decouple import config
import tweepy

bearer_token = config('TWITTER_BEARER_TOKEN')
api_key = config('TWITTER_API_KEY')
api_secret = config('TWITTER_API_SECRET')
access_token = config('ACCESS_TOKEN')
access_token_secret = config('ACCESS_TOKEN_SECRET')
USERNAME = 'veritanonbugia'
USER_ID = 1457371398507220993


class SimpleTwitter:

    def __init__(self):
        self.api = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_secret,
                                 access_token=access_token, access_token_secret=access_token_secret)

    def get_user(self):
        return self.api.get_user(username=USERNAME)

    def get_user_tweets(self):
        return self.api.get_users_tweets(id=USER_ID)

    def tweet(self):
        try:
            self.api.create_tweet(text='this is a test tweet')
            print('successfully created tweet')
        except Exception as E:
            print(E)


client = SimpleTwitter()
# client.tweet()

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print(tweet.text)
