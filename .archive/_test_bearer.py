#!/usr/bin/env python3
"""Test generating a bearer token for X API"""
import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('X_API_KEY')
secret = os.getenv('X_API_SECRET')
if not key or not secret:
    print('Missing X_API_KEY or X_API_SECRET')
    sys.exit(1)

b64 = base64.b64encode(f'{key}:{secret}'.encode()).decode()
req = urllib.request.Request(
    'https://api.twitter.com/oauth2/token',
    data=b'grant_type=client_credentials',
    headers={
        'Authorization': f'Basic {b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    method='POST'
)
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    if 'access_token' in data:
        print('SUCCESS: Bearer token generated')
        print('BEARER_TOKEN=' + data['access_token'])
    else:
        print('No access_token in response:', json.dumps(data, indent=2)[:500])
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.reason}')
    body = e.read().decode()
    print('Body:', body[:500])
except Exception as e:
    print(f'Error: {e}')
