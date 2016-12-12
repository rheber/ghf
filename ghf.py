import json
from urllib.request import urlopen

URL = 'https://api.github.com/users/{user}/following?page={pageNum}&per_page=100'
user = 'rheber'
pageNum = 1

def main():
  response = urlopen(URL.format(user=user, pageNum=pageNum)).read()
  followedUsernames = [user['login'] for user in json.loads(response.decode())]
  for username in followedUsernames:
    print(username)

main()
