'''GUI elements.'''

import os.path
import sys
import tkinter as tk
from urllib.error import URLError
from api import followeeNames
from serde import loadFollowees

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

class App():
    '''Root window of the GUI.'''

    def __init__(self, config):
        def followeesPath(config) -> str:
            '''Return followees file name and folder.'''
            return os.path.join(config['followeesFolder'], config['followeesFilename'])

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
            users = sorted(followeeNames(yourname), key=(lambda x: x.lower()))
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
