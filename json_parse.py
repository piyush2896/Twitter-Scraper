import six
import json
from collections import defaultdict

import pandas as pd
import requests
from requests_oauthlib import OAuth1

def _convert_to_utf8_str(arg):
    if isinstance(arg, six.text_type):
        return arg.encode('utf-8')
    if not isinstance(arg, bytes):
        return six.text_type(arg).encode('utf-8')
    return arg

def apply_auth(consumer_key,
               consumer_secret,
               access_token,
               access_token_secret):
    return OAuth1(consumer_key,
                  client_secret=consumer_secret,
                  resource_owner_key=access_token,
                  resource_owner_secret=access_token_secret,
                  decoding=None)

def get_session(count=10):
    session = requests.Session()
    session.headers['Accept-encoding'] = 'gzip'
    session.params['count'] = _convert_to_utf8_str(count)
    return session

def get_public_tweets(auth, count):
    root_url = 'api.twitter.com'
    endpoint = '/statuses/home_timeline.json'
    upload_root = '/1.1'

    session = get_session(count)

    url = 'https://' + root_url + upload_root + endpoint
    resp = session.request('GET', url, auth=auth, proxies='')
    return resp.json()


def parse_json(json_obj):
    return json_obj['id_str'], json_obj['text']

def parse_to_csv(path, public_tweets):
    df_data = defaultdict(lambda: [])

    for tweet_i, tweet in enumerate(public_tweets):
        tweet_id, tweet_text = parse_json(tweet)
        df_data['S.no'].append(tweet_i)
        df_data['tweetid'].append(tweet_id)
        df_data['tweettext'].append(tweet_text)

    df = pd.DataFrame(df_data, columns=['S.no', 'tweetid', 'tweettext'])
    df.to_csv(path, index=False)

def get_tweets_and_generate_csv(consumer_key,
                                consumer_secret,
                                access_token,
                                access_token_secret,
                                count=10):
    print('* Preparing Auth')
    auth = apply_auth(consumer_key,
                      consumer_secret,
                      access_token,
                      access_token_secret)
    print('* Collecting tweets')
    public_tweets_json = get_public_tweets(auth, count)
    print('* Generating CSV')
    parse_to_csv('tweets.csv', public_tweets_json)

if __name__ == '__main__':
    creds = json.load(open('credentials.json'))
    get_tweets_and_generate_csv(creds['consumer_key'],
                                creds['consumer_secret'],
                                creds['access_token'],
                                creds['access_token_secret'],
                                100)
