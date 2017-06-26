# -*- coding: utf-8 -*-
import boto3
import json
import logging
import os
import datetime
import tmdbsimple as tmdb

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def response(err, speech=None):
    json_body = {
        "speech": speech,
        "displayText": speech,
        # "contextOut": [],
        # "data": data,
        "source": "apiai-top-movie-webhook"
    }

    # add http headers
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(json_body),
        # 'body': err.message if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

'''
event:
{
    "body":
    "headers":
    "method":
    "params":
    "query":
}
'''
def lambda_handler(event, context):

    if (event is None):
        return response(None, "nothing")

    # check api key
    if (event.get('headers').get('isobar-api-key')!=os.environ['ISOBAR_API_KEY']):
        return response(None, "key error")

    if (event.get('body') is None):
        return response(None, "no body")

    raw_body = event.get('body')
    body = json.loads(raw_body)
    result = body.get('result')

    # print("Received event: " + json.dumps(event, indent=2))
    # return response(Exception('Invalid request token'))

    # print("API KEY: "+os.environ['TMDB_API_KEY'])
    tmdb.API_KEY = os.environ['TMDB_API_KEY']

    # current year
    now_year = datetime.datetime.now().year

    # language
    lang = 'zh-TW'
    # searching-movie-by-date
    # print("Action: "+ event["result"]["action"])
    action = result["action"]
    # params
    date = result["parameters"]["date"][:4]
    if (len(date)<1):
        date = now_year
    # print("Period: "+ event["result"]["parameters"]["date-period"])
    # print("year: "+ event["result"]["parameters"]["date-period"][:4])
    period = result["parameters"]["date-period"][:4]
    if (len(period)<1):
        period = date

    # discover top 10
    discover = tmdb.Discover()

    speech = ''
    if (action=='searching-movie-by-date'):
        result = discover.movie(page=1, sort_by="popularity.desc",language=lang,year=period)
        for m in result['results'][:10]:
            speech = speech + m['title'] + ','
    if (len(speech) > 0):
        speech = str(period)+'年 好看的電影如下 '+speech
        return response(None, speech[:-1])
    else:
        return response(None, '')
