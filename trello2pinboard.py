import os
import argparse
import json
import requests
import re
from urllib.parse import urlencode

USER = '' # your pinboard.io username
TOKEN = '' # get your token (starting after the colon) from here: https://pinboard.in/settings/password

API_URL = 'https://api.pinboard.in/v1/posts/add'
# src: https://stackoverflow.com/a/28552670
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

def load_json():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Trello json export file")
    args = parser.parse_args()

    with open(args.file) as fp:
        return json.load(fp)

def add(tag, desc, url, user, token):
    query_string = urlencode(dict(url=url.strip(),description=desc.strip(),tags=tag.strip(),auth_token=user+":"+token))
    url = API_URL + "?" + query_string
    return requests.get(url)

if __name__ == "__main__":
    content = load_json()

    lists = dict()
    for listitem in content['lists']:
        lists[listitem['id']] = listitem['name']

    cards = []
    for card in content['cards']:
        card_list_name = lists[card['idList']]

        # try to find url in desc or name
        urls = re.findall(URL_REGEX, card['desc'])
        desc = card['desc']
        if not urls:
            urls = re.findall(URL_REGEX, card['name'])
        if not urls:
            print('No URL found, skipping card', card['desc'], card['name'])
            continue
        url = urls[0]

        if desc == '':
            desc = url

        cards.append((card_list_name, desc, url))

    if USER:
        user = USER
    else:
        user = input('Username: ')

    if TOKEN:
        token = TOKEN
    else:
        token = input('Token: ')

    print('Found {} cards containing urls in {} lists'.format(len(cards), len(lists)))
    ok = input('Add {} cards to pinboard as user {}? y/n: '.format(len(cards), user))

    if(ok == 'y'):
        for i, (card_list, desc, url) in enumerate(cards):
            response = add(card_list, desc, url, user, token)
            print(i, response.text)
            if not "done" in response.text or response.status_code != 200:
                print(card_list, desc, url)
    else:
        exit()
    
