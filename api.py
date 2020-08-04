'''Functions for interacting with the Github API.'''

import json
from typing import Iterable
from urllib.request import urlopen

URL = 'https://api.github.com/users/{user}/following?page={pageNum}&per_page=100'
pageNum = 1

def followeeNames(user: str) -> Iterable[str]:
    '''Get followee usernames from Github.'''
    response = urlopen(URL.format(user=user, pageNum=pageNum)).read()
    followedUsernames = [user['login'] for user in json.loads(response.decode())]
    return (u for u in followedUsernames)
