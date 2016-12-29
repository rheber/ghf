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

class App(tk.Tk):
  def __init__(self):
    root = tk.Tk.__init__(self)
    self.populateTable(root)

  def populateTable(self, root):
    try:
      users = list(usernames())
    except URLError:
      users = ['Could not fetch user list.']
    ulen = len(users)
    self.frame = ScrolledFrame(root, rows=ulen)
    self.frame.pack()
    for i in range(ulen):
      self.frame.interior.set(i, 0, users[i])

def gui():
  return App().mainloop()

def main():
  return gui()

if __name__ == '__main__':
  main()
