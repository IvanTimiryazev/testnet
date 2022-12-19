import re
import snscrape.modules.twitter as snstwitter
import datetime
import pytz
import time
from config import Config


limit = 100


def scrap(sources: list, regs):
    now = datetime.datetime.now(tz=pytz.utc)
    start = time.time()
    tweets = []
    since = now - datetime.timedelta(days=Config.TIME_INTERVAL)
    for acc in sources:
        print(acc)
        query = f'(from:{acc} since:{since.strftime("%Y-%m-%d")} until:{now.strftime("%Y-%m-%d")})'
        print(query)
        for tweet in snstwitter.TwitterSearchScraper(query).get_items():
            tweets.append({'url': tweet.url, 'content': tweet.content, 'date': tweet.date})
    print(tweets)
    print("--- %s seconds ---" % (time.time() - start))
    print(len(tweets))
    return parser(tweets, regs)


def parser(tweets, regs):
    print(regs)
    r = '|'.join(regs)
    print(r)
    regex = fr'^(?=.*({r})).*$'
    print(regex)
    matched = []
    for i in tweets:
        raw_text = i['content'].split()
        raw_text = ' '.join(raw_text).lower()
        parse_result = re.match(regex, raw_text)
        if parse_result:
            matched.append(i)
    print(matched)
    return matched


# if __name__ == '__main__':
#     scrap()


