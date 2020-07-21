#!/usr/bin/env python3

'''
ghf: A program for annotating Github followees.
'''

import json
from os import environ
import os.path
import sys
import tkinter as tk
from typing import Dict, Iterable, Optional, Tuple
from urllib.error import URLError
from urllib.request import urlopen

URL = 'https://api.github.com/users/{user}/following?page={pageNum}&per_page=100'
pageNum = 1

class ghfException(Exception):
    '''Custom exception.'''

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

def followeeNames(user: str) -> Iterable[str]:
    '''Get followee usernames from Github.'''
    response = urlopen(URL.format(user=user, pageNum=pageNum)).read()
    followedUsernames = [user['login'] for user in json.loads(response.decode())]
    return (u for u in followedUsernames)

def followeesPath(config) -> str:
    '''Return followees file name and folder.'''
    return os.path.join(config['followeesFolder'], config['followeesFilename'])

class TableAnnotated(tk.Frame):
    '''Table with one column of labels and one of entry boxes.'''

    def __init__(self, parent, rows=5):
        tk.Frame.__init__(self, parent)
        self.widgets = []
        for row in range(rows):
            label = tk.Label(self)
            label.grid(row=row, column=0)
            entry = tk.Entry(self)
            entry.grid(row=row, column=1)
            self.widgets.append([label, entry])

    def get(self, row, col):
        '''Get the value of the cell at the specified coordinates.'''
        return self.widgets[row][0]['text'] if col == 0 else self.widgets[row][1].get()

    def set(self, row, col, value):
        '''Set the value of the cell at the specified coordinates.'''
        widget = self.widgets[row][col]
        if col == 0:
            widget.configure(text=value)
        else:
            widget.delete(0, tk.END)
            widget.insert(0, value)

class ScrolledFrame(tk.Frame):
    '''Element with scrollbar.'''

    def __init__(self, parent, rows=30):
        tk.Frame.__init__(self, parent)

        vscroll = tk.Scrollbar(self, orient='vertical')
        vscroll.pack(expand='false', fill='y', side='right')
        canvas = tk.Canvas(self, bd=0, yscrollcommand=vscroll.set)
        canvas.pack(expand='true', fill='both', side='left')
        vscroll.config(command=canvas.yview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = intr = TableAnnotated(canvas, rows)
        interiorId = canvas.create_window(0, 0, anchor='nw', window=intr)

        def configure_interior(_event):
            w, h = (intr.winfo_reqwidth(), intr.winfo_reqheight())
            canvas.config(scrollregion="0 0 {0} {1}".format(w, h))
            if w != h:
                canvas.config(width=w)
        intr.bind('<Configure>', configure_interior)

        def configure_canvas(_event):
            if intr.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interiorId, width=canvas.winfo_width())
        canvas.bind('<Configure>', configure_canvas)

def loadFollowees(path: str) -> Dict[str, str]:
    '''Dictionary of names and descriptions in followees file.'''

    def ud(line: str) -> Tuple[str, str]:
        '''Break liine into user and description.'''
        sp = line.split('\t')
        if len(sp) == 0:
            return ('', '')
        if len(sp) == 1:
            return (sp[0], '')
        return (sp[0], sp[1])

    try:
        return {ud(line)[0]:ud(line)[1] for
                line in list(open(path).read().split('\n')) if line}
    except FileNotFoundError:
        with open(path, 'w') as fo:
            fo.write('')
        return {}
    except IndexError:
        raise ghfException('Error reading followees file.')

class App():
    '''Root window of the GUI.'''

    def __init__(self, config):
        self.root = tk.Tk()
        self.root.title('ghf')
        self.followeesPath = followeesPath(config)
        self.amtRows = self.populateTable(config['username'])
        self.createButtons()

    def run(self):
        '''Run the Tk main loop.'''
        return self.root.mainloop()

    def saveFollowees(self):
        '''Save data to followees file.'''
        table = self.frame.interior
        with open(self.followeesPath, 'w') as fo:
            fo.writelines('{0}\t{1}\n'.format(
                table.get(row, 0), table.get(row, 1)) for row in range(self.amtRows))

    def createButtons(self):
        '''Create save button.'''
        btnSave = tk.Button(self.root, text='Save', command=self.saveFollowees)
        btnSave.pack(side='bottom')

    def populateTable(self, yourname):
        '''Fills table. Returns amount of rows.'''
        try:
            users = sorted(list(followeeNames(yourname)))
            ulen = len(users)
            f = loadFollowees(self.followeesPath)
            descs = []
            for user in users:
                if user in f:
                    descs.append(f[user])
                else:
                    descs.append('')
            print(
                'Successfully retrieved {0}\'s data from Github.'.format(yourname),
                file=sys.stderr
            )
        except URLError:
            f = sorted(loadFollowees(self.followeesPath).items())
            users = list(map(lambda x: x[0], f))
            descs = list(map(lambda x: x[1], f))
            ulen = len(users)
            print('Could not load {0}\'s data from Github.'.format(yourname), file=sys.stderr)
        self.frame = ScrolledFrame(self.root, rows=ulen)
        self.frame.pack()
        for i in range(ulen):
            self.frame.interior.set(i, 0, users[i])
            self.frame.interior.set(i, 1, descs[i])
        return ulen

def gui(config):
    '''Launch the GUI.'''
    return App(config).run()

def main():
    '''Main function.'''
    config = readConfig()
    config['username'] = yourName(config)
    return gui(config)

if __name__ == '__main__':
    main()
