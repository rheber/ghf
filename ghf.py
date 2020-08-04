#!/usr/bin/env python3

'''
ghf: A program for annotating Github followees.
'''

import json
from os import environ
import os.path
from typing import Optional
from gui import App

def readConfig():
    '''Return configuration object.'''

    path = pathIfFound('ghf.json')
    if path:
        with open(path) as fyle:
            config = json.loads(fyle.read())
        if 'followeesFilename' not in config:
            config['followeesFilename'] = 'followees'
        if 'followeesFolder' not in config:
            config['followeesFolder'] = '.'
    else:
        config = {}
        config['followeesFilename'] = 'followees'
        config['followeesFolder'] = '.'

    return config

def pathIfFound(filename: str) -> Optional[str]:
    '''Full path if file in current folder or any folder in system path.'''
    pathFolders = environ['PATH'].split(';') # Not tested on Unix.
    pathFolders.insert(0, '.')
    for folder in pathFolders:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return path
    return None

def yourName(config) -> str:
    '''Prompt user for their Github username or get it from configuration.'''
    if 'username' in config:
        return config['username']
    return input('Enter your username: ')


def main():
    '''Main function.'''
    config = readConfig()
    config['username'] = yourName(config)
    return App(config).run()

if __name__ == '__main__':
    main()
