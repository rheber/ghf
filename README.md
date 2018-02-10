# README

ghf is a tool that gets the list of people you follow on Github, allowing you to keep notes on them.

## Usage

Run `python ghf.py` and enter your username. A window listing your Github followees will appear. Beside each username will be a text box. Clicking the Save button will save the list of users along with your annotations to file.

## Configuration

By default, ghf will save your notes to a file in the current directory. To customise this behaviour:

1. Rename ghf.sample.json to ghf.json.
1. Place the file anywhere in your current directory or system path.
1. Modify the values inside the file.

## Type Checking

If you've installed mypy, you can perform type checking by running `python -m mypy ghf.py`.
