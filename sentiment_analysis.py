import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import statistics
import requests
import click
from secrets import *

# https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python



class Twitter:
    def __init__(self):
        """
        Returns the tweepy api object

        # TODO Move the keys to env variables

        Args:

        Returns:
            Tweepy object
        """
        self.consumer_key = CONSUMER_KEY
        self.consumer_secret = CONSUMER_SECRET
        self.access_token = ACCESS_TOKEN
        self.access_token_secret = ACCESS_TOKEN_SECRET

    def connect(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        return api


def analyse(search_term):
    api = Twitter().connect()
    search_results = api.search(q=search_term, count=1000)
    # also checkout https://github.com/sloria/TextBlob
    sid_obj = SentimentIntensityAnalyzer()
    result = {}
    scores = []

    for tweet in search_results:
        scores.append([sid_obj.polarity_scores(tweet.text).get("compound"), tweet.text])
    if len(scores) > 1:
        mean_scores = statistics.mean([score[0] for score in scores])
        result['mean_score'] = mean_scores
        scores.sort(key=lambda a: a[0])
        # TODO Word cloud, time-series graph,popular positive/negative tweets, +ve -ve tweets by popular users
        result['top_positive_tweets'] = scores[-5:]
        result['top_negative_tweets'] = scores[:5]
    return result



@click.command()
@click.argument('location')
def main(location):
    geo_code_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={OPEN_CAGE_KEY}"
    response = requests.get(geo_code_url).json()
    lat = response['results'][0]['geometry']['lat']
    lng = response['results'][0]['geometry']['lng']
    print(location)
    results = analyse(f"Coronavirus geocode:{lat},{lng},50km -filter:retweets")
    mean_score = results['mean_score']
    if mean_score < -0.05:
        print(colorize(f"Sentiment is generally negative {mean_score}",bcolors.FAIL))
    elif mean_score > 0.05:
        print(colorize(f"Sentiment seems generally positive {mean_score}",bcolors.OKGREEN))
    else:
        print(colorize(f"Sentiment seems neutral {mean_score}",bcolors.OKBLUE))
    print(colorize(f"Some top Positive tweets are:",bcolors.OKGREEN))
    for x in results['top_positive_tweets']:
        print(x[1])
    print(colorize(f"Some top negative tweets are:",bcolors.FAIL))
    for x in results['top_negative_tweets']:
        print(x[1])

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colorize(text,color_type):

    return f'{color_type}{text}{bcolors.ENDC}'

if __name__ == "__main__":
    main()