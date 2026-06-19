#!/usr/bin/env python3
import os

import tweepy
from dotenv import load_dotenv

load_dotenv()

client = tweepy.Client(
    consumer_key=os.getenv('X_API_KEY'),
    consumer_secret=os.getenv('X_API_SECRET'),
    access_token=os.getenv('X_ACCESS_TOKEN'),
    access_token_secret=os.getenv('X_ACCESS_TOKEN_SECRET'),
    wait_on_rate_limit=True
)
try:
    me = client.get_me()
    print(f'OK: @{me.data.username} (id={me.data.id})')
except Exception as e:
    print(f'FAIL: {e}')
