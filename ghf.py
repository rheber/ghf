import json
from os import environ
import os.path
import tkinter as tk
from urllib.error import URLError
from urllib.request import urlopen

URL = 'https://api.github.com/users/{user}/following?page={pageNum}&per_page=100'
pageNum = 1

YOURNAME = ''

def pathIfFound(filename):
  '''Full path if file in current folder or any folder in system path.'''
  pathFolders = environ['PATH'].split(';') # Not tested on Unix.
  pathFolders.insert(0, '.')
  for folder in pathFolders:
    path = os.path.join(folder, filename)
    if os.path.exists(path):
      return path

def yourName():
  '''Prompt user for their Github username.'''
  return input('Enter your username: ')

def followeeNames():
  '''Get followee usernames from Github.'''
  global YOURNAME
  user = YOURNAME
  response = urlopen(URL.format(user=user, pageNum=pageNum)).read()
  followedUsernames = [user['login'] for user in json.loads(response.decode())]
  return (u for u in followedUsernames)

def followeesPath():
  '''Return followees file name and folder.'''

  # Defaults
  followeesFilename = 'followees'
  followeesFolder = '.'

  path = pathIfFound('ghf.json')
  if path:
    with open(path) as fyle:
      config = json.loads(fyle.read())
    if 'followeesFilename' in config:
      followeesFilename = config['followeesFilename']
    if 'followeesFolder' in config:
      followeesFolder = config['followeesFolder']

  return os.path.join(followeesFolder, followeesFilename)

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
    return self.widgets[row][0]['text'] if col == 0 else self.widgets[row][1].get()

  def set(self, row, col, value):
    widget = self.widgets[row][col]
    if col == 0:
      widget.configure(text=value)
    else:
      widget.delete(0, tk.END)
      widget.insert(0, value)

class ScrolledFrame(tk.Frame):
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

    def configure_interior(event):
      w, h = (intr.winfo_reqwidth(), intr.winfo_reqheight())
      canvas.config(scrollregion="0 0 {0} {1}".format(w, h))
      if w != h:
        canvas.config(width=w)
    intr.bind('<Configure>', configure_interior)

    def configure_canvas(event):
      if intr.winfo_reqwidth() != canvas.winfo_width():
        canvas.itemconfigure(interiorId, width=canvas.winfo_width())
    canvas.bind('<Configure>', configure_canvas) 

def loadFollowees():
  '''Dictionary of names and descriptions in followees file.'''

  def ud(line):
    '''Break liine into user and description.'''
    sp = line.split('\t')
    if len(sp) == 0:
      return ('', '')
    if len(sp) == 1:
      return (sp[0], '')
    return (sp[0], sp[1])

  try:
    return {ud(line)[0]:ud(line)[1] for
            line in list(open(followeesPath()).read().split('\n')) if line}
  except FileNotFoundError:
    return {'Could not fetch user list or open followees file.':''}
  except IndexError:
    return {'Error reading followees file.':''}

class App(tk.Tk):
  def __init__(self):
    root = tk.Tk.__init__(self)
    self.title('ghf')
    self.amtRows = self.populateTable(root)
    self.createButtons()

  def saveFollowees(self):
    table = self.frame.interior
    with open(followeesPath(), 'w') as fo:
      fo.writelines('{0}\t{1}\n'.format(
        table.get(row, 0), table.get(row, 1)) for row in range(self.amtRows))

  def createButtons(self):
    btnSave = tk.Button(self, text='Save', command=self.saveFollowees)
    btnSave.pack(side='bottom')

  def populateTable(self, root):
    '''Fills table. Returns amount of rows.'''
    global YOURNAME
    try:
      users = sorted(list(followeeNames()))
      ulen = len(users)
      f = loadFollowees()
      descs = []
      for user in users:
        descs.append(f[user]) if user in f else descs.append('')
      print('Successfully retrieved {0}\'s data from Github.'.format(YOURNAME))
    except URLError:
      f = sorted(loadFollowees().items())
      users = list(map(lambda x: x[0], f))
      descs = list(map(lambda x: x[1], f))
      ulen = len(users)
      print('Could not load {0}\'s data from Github.'.format(YOURNAME))
    self.frame = ScrolledFrame(root, rows=ulen)
    self.frame.pack()
    for i in range(ulen):
      self.frame.interior.set(i, 0, users[i])
      self.frame.interior.set(i, 1, descs[i])
    return ulen

def gui():
  return App().mainloop()

def main():
  global YOURNAME
  YOURNAME = yourName()
  return gui()

if __name__ == '__main__':
  main()
