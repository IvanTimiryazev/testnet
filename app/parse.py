import re
import snscrape.modules.twitter as snstwitter

tweets = []
limit = 30


def scrap(sources: list, regs):
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
















