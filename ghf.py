import json
import tkinter as tk
from urllib.error import URLError
from urllib.request import urlopen

URL = 'https://api.github.com/users/{user}/following?page={pageNum}&per_page=100'
user = 'rheber'
pageNum = 1

def usernames():
  response = urlopen(URL.format(user=user, pageNum=pageNum)).read()
  followedUsernames = [user['login'] for user in json.loads(response.decode())]
  return (u for u in followedUsernames)

class Table(tk.Frame):
  def __init__(self, parent, rows=5, cols=2):
    tk.Frame.__init__(self, parent)
    self.widgets = []
    for row in range(rows):
      currentRow = []
      for col in range(cols):
        label = tk.Label(self, text='_')
        label.grid(row=row, column=col)
        currentRow.append(label)
      self.widgets.append(currentRow)

  def get(self, row, col):
    return self.widgets[row][col]['text']

  def set(self, row, col, value):
    widget = self.widgets[row][col]
    widget.configure(text=value)

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

    self.interior = intr = Table(canvas, rows)
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
    sp = line.split()
    if len(sp) == 0:
      return ('', '')
    if len(sp) == 1:
      return (sp[0], '')
    return (sp[0], sp[1])

  try:
    return {ud(line)[0]:ud(line)[1] for
            line in list(open('followees').read().split('\n')) if line}
  except FileNotFoundError:
    return {'Could not fetch user list or open followees file.':''}
  except IndexError:
    return {'Error reading followees file.':''}

class App(tk.Tk):
  def __init__(self):
    root = tk.Tk.__init__(self)
    self.amtRows = self.populateTable(root)
    self.createButtons()

  def saveFollowees(self):
    table = self.frame.interior
    with open('followees', 'w') as fo:
      fo.writelines('{0}\t{1}\n'.format(
        table.get(row, 0), table.get(row, 1)) for row in range(self.amtRows))

  def createButtons(self):
    btnSave = tk.Button(self, text='Save', command=self.saveFollowees)
    btnSave.pack(side='bottom')

  def populateTable(self, root):
    '''Fills table. Returns amount of rows.'''
    try:
      users = list(usernames())
      ulen = len(users)
      f = loadFollowees()
      descs = []
      for user in users:
        descs.append(f[user]) if user in f else descs.append('_')
    except URLError:
      f = loadFollowees()
      users = list(f.keys())
      descs = list(f.values())
      ulen = len(users)
    self.frame = ScrolledFrame(root, rows=ulen)
    self.frame.pack()
    for i in range(ulen):
      self.frame.interior.set(i, 0, users[i])
      self.frame.interior.set(i, 1, descs[i])
    return ulen

def gui():
  return App().mainloop()

def main():
  return gui()

if __name__ == '__main__':
  main()
