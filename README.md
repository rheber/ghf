# README

ghf is a tool that gets the list of people you follow on Github, allowing you to keep notes on them.

## Setup

ghf was written in Python 3.5 and uses tkinter.

### Windows

Download and run the latest Python 3.5 installer from the Python website, which should automatically install tkinter.

### Debian

At the time of writing, running `apt-get install python3` installs Python 3.5 on Debian.

Additionally, you'll need to run `apt-get install python3-tk` to get tkinter.

## Usage

1. Run `python3 ghf.py`. Alternatively, if `ghf.py` is set to be executable you can run `./ghf.py`.

2. Enter your username.

3. A window listing your Github followees will appear. Beside each username will be a text box in which you may write a note.

4. Click the Save button to save the list of users along with your annotations to file.

## Configuration

By default, ghf will save your notes to a file in the current directory. To customise this behaviour:

1. Rename ghf.sample.json to ghf.json.

2. Place the file anywhere in your current directory or system path.

3. Modify the values inside the file.

## Type Checking

If you've installed mypy, you can perform type checking by running `python3 -m mypy ghf.py`.
