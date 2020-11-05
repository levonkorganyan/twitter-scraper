from datetime import datetime, timedelta
from email.utils import parsedate_tz

import base64
import pandas as pd
import numpy as np 
import requests
import tweepy
import argparse
import datetime
import json
import os

class Api:
    def __init__(self):
        self.api_key, self.api_key_secret, self.access_token, self.access_token_secret = Api._load_config()
        self.tweepy_api = None

    @staticmethod
    def _load_config():
        configs_to_target = ['ApiKey', 'ApiKeySecret', 'AccessToken', 'AccessTokenSecret']

        with open('config') as config:
            lines = config.readlines()
            if len(lines) != len(configs_to_target):
                raise Exception('incorrect number of config keys ({}), expecting the following: {}'.format(len(lines), configs_to_target))

            def _find_value(config):
                found = [line for line in lines if config in line]
                if not found:
                    raise Exception('missing expected config {}', config)
                return found[0].replace(config + '=', '').rstrip()

            return (_find_value(config) for config in configs_to_target)

    
    def _get_api(self):
        if not self.tweepy_api:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.tweepy_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        return self.tweepy_api

    @staticmethod
    def _date_string(dt):
        return datetime.datetime.strftime(dt, '%Y-%m-%d')


    def get_tweets_for_hashtag(self, hashtag, since, until=datetime.datetime.now(), filter_retweets=False):
        query = hashtag + (' -filter:retweets' if filter_retweets else '')
        return tweepy.Cursor(
            self._get_api().search,
            q=query,
            lang="en",
            since=Api._date_string(since),
            until=Api._date_string(until),
            tweet_mode='extended').pages()