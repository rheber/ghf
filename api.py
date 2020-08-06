'''Functions for interacting with the Github API.'''

import json
from typing import Iterable
from urllib.request import urlopen

userUrl = 'https://api.github.com/users/{user}'
followingUrl = 'https://api.github.com/users/{user}/following?page={pageNum}&per_page=100'

def followeeNames(user: str) -> Iterable[str]:
    '''Get followee usernames from Github.'''
    userResponse = urlopen(userUrl.format(user=user)).read()
    userJson = json.loads(userResponse.decode())
    followingAmount = userJson['following']
    followedUsernames = []
    for pageNum in range(1 + followingAmount // 100):
        response = urlopen(followingUrl.format(user=user, pageNum=(1+pageNum))).read()
        followedUsernames.extend([user['login'] for user in json.loads(response.decode())])
    print("Retrieved {0} usernames from Github.".format(len(followedUsernames)))
    return followedUsernames
