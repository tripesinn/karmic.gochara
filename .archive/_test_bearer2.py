#!/usr/bin/env python3
import base64
import json
import os
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv()
ak = os.getenv('X_API_KEY')
sk = os.getenv('X_API_SECRET')
b64 = base64.b64encode(f'{ak}:{sk}'.encode()).decode()
req = urllib.request.Request(
    'https://api.twitter.com/oauth2/token',
    data=urllib.parse.urlencode({'grant_type': 'client_credentials'}).encode(),
    headers={'Authorization': f'Basic {b64}', 'Content-Type': 'application/x-www-form-urlencoded'},
    method='POST'
)
try:
    resp = urllib.request.urlopen(req)
    print('OK:', json.loads(resp.read()))
except Exception as e:
    print(f'Erreur: {e}')
