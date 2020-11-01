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
import pprint
import click


from api import Api
import pdb

@click.group()
def cli():
    pass

@click.command()
@click.argument('setname', type=str)
@click.argument('hashtag', type=str)
@click.argument('since_days_ago', type=int)
@click.option('--until_days_ago', type=int, default=0, help='0 means until today (default 0)')
def create(setname, hashtag, since_days_ago, until_days_ago):
    if since_days_ago < 0:
        since_days_ago = 1
    if until_days_ago < 0:
        until_days_ago = 0
    if not hashtag:
        raise Exception('Invalid hashtag {}', hashtag)
    if hashtag[0] != '#':
        hashtag = '#' + hashtag
    set_path = os.path.join('data', setname)
    if not os.path.exists(set_path):
        os.makedirs(set_path)
    else:
        raise Exception('Set "{}" already exists, use `resume` command'.format(setname))
    run(hashtag, since_days_ago, until_days_ago, set_path)


@click.command()
@click.argument('setname')
def resume(setname):
    data_path = 'data'
    if not os.path.isdir(data_path):
        raise Exception('No data found')
    set_path = os.path.join(data_path, setname)
    if not os.path.isdir(set_path):
        raise Exception('Set {} not found', setname)
    files = os.listdir(set_path)
    if not files:
        raise Exception('No data found in set {}', setname)
    files.sort(reverse=True)

    hashtag = None
    since = None
    until = None
    for i in range(len(files)):
        last_file = files[i]
        with open(last_file, 'r') as inputfile:
            try:
                data = json.load(inputfile)
                if not 'request' in data:
                    continue
                request = data['request']
                if not 'until' in request:
                    continue
                until = request['until']
                if not 'hashtag' in request:
                    continue
                hashtag = request['hashtag']
                if not 'items' in request:
                    continue
                items = request['items']
                if len(items) == 0:
                    continue
                first_item = items[0]
                since = first_item.created_at
            except ValueError:
                continue
    if not hashtag or not since or not until:
        raise Exception('No valid data found in set {}, cannot resume', setname)
    run(hashtag, since, until, set_path)


cli.add_command(create)
cli.add_command(resume)


def write_page(cursor, request, items, path, mapper=lambda x: x):
    data = { 
        'cursor': cursor,
        'items': [mapper(item) for item in items],
        'request': request
    }
    filename = str(datetime.datetime.now().timestamp()).replace('.', '_') + '.json'
    full_path = os.path.join(path, filename)
    print('Writing to location {}'.format(full_path))
    with open(full_path, 'w') as outputfile:
        json.dump(data, outputfile)


def run(hashtag, since, until, path):
    api = Api()
    request = {
        'hashtag': '#DontBelieveArmenia',
        'since': since,
        'until': until
    }
    days_since = datetime.datetime.now() - datetime.timedelta(since)
    days_until = datetime.datetime.now() - datetime.timedelta(until)
    for page in api.get_tweets_for_hashtag(hashtag, days_since, days_until):
        if len(page) == 0:
            return
        page.reverse()
        start_time = page[0].created_at.timestamp()
        write_page(start_time, request, page, path, mapper=lambda s: s._json)


if __name__ == '__main__':
    cli()