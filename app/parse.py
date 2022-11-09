import re
import snscrape.modules.twitter as snstwitter

tweets = []
limit = 30
regex = r'^(?=.*(yankees)).*$'


def scrap(sources: list):
    for acc in sources:
        count = 0
        print(acc)
        query = f'(from:{acc})'
        print(query)
        for tweet in snstwitter.TwitterSearchScraper(query).get_items():
            if len(tweets) == limit:
                break
            else:
                tweets.append({'url': tweet.url, 'content': tweet.content})
    print(tweets)
    return parser(tweets)


def parser(tweets):
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
















