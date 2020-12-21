#!/usr/bin/env python3
'''
Store all your text snippets to a file.
Use keywords to find your snippets easily back
I use it to store all kind of coding fragments.
But also for installation instructions, and even for cooking recepts and all kind of things I always forget
You can also edit the notefile with your favorite editor 

note.py            add note snippets to a file
note.py -s regexp  search items from the saved snippets

edit '--dir' argument to set your note directory path permanent

20201221 2.0  primus  now with multiple search items
20201213 1.9  primus  with option to attach files to notes
20201209 1.8  primus  rewritten as class
20180918 1.7  primus  replace non ascii chars with "~"
20161129 1.4  primus  split db file per year
20150722 1.1  primus  keyword argumenten included
20150715 1.0  primus  port from perl
'''
__version__ = '2.0'

import re, os, sys
import datetime
import argparse
import logging
import shutil
import pathlib 

class notes(object):

  def __init__(self, args):
    self.args   = args
    self.files  = []
    self.report = []
    self.stamp  = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    self.year   = datetime.datetime.now().strftime('%Y')
    self.check_dir(self.args.dir)
    self.db  = os.path.join(self.args.dir, 'notes{}.db'.format(self.year))    # current note file
    self.filestore = os.path.join(self.args.dir, 'notes{}'.format(self.year)) # path to store appended files
    self.check_dir(self.filestore)
    for db in os.listdir(self.args.dir):
      if re.search ('notes[0-9]{4}.db', db):
        self.files.append(os.path.join(self.args.dir, db))
    if self.args.search:           # search in notes
      for i in self.args.keywords: # append all unspecified keyword arguments to the search items, all must be found in the snipped
        self.args.search.append(i)
      for fn in self.files:
        self.searchfile(fn) 
    else:                          # add new note
      self.newnote()

     
  def check_dir(self, path):       # check if the directory exists otherwise create it
    if not os.path.exists(path):
      try:
        os.mkdir(path)
      except OSError as e:
        logging.error('mkdir {} failed: {}'.format(path, e))

  def __repr__(self):
     return '\n'.join(map(str,self.report))
  
  def newnote(self):
    hdr = '### {} {}'.format(self.stamp, ' '.join(map(str, self.args.keywords)))
    print('keywords {}'.format(' '.join(map(str, self.args.keywords))))
    print('enter text for the new note, end with met ctrl-z or ctrl-d')
    with open(self.db, 'a') as fh:
      fh.write('\n{}\n'.format(hdr))
      for line in sys.stdin:
#        line=re.sub(r'[^\x09-\x7e]','~',line)  # strip all kind of junk
        fh.write(line)
      if self.args.file:
        for i, fn in enumerate (self.args.file):
          if os.path.exists(fn):
            fs = '{}-{:02d}{}'.format(self.stamp, i+1, pathlib.Path(fn).suffix.lower())
            fh.write('\n{{{{ {} }}}}'.format(fs))
            shutil.copy(fn, os.path.join(self.filestore, fs))
          else:
            logging.error('file {} not found'.format(fn)) 

  def searchblok(self, blok):
    hit = []
    line_cnt = [0, ]
    for j, s in enumerate(self.args.search):
      hit.append(False)
      for i ,line in enumerate(blok):
        if re.search(s, line, re.I):   # ignore case
          hit[j] = True
          line_cnt.append(i)
    for h in hit:
      if not h:  # block must contain all search items
        return
    for i ,line in enumerate(blok):
      if i in line_cnt or not self.args.line: # report line if it contains any of the search items or is the first line
         self.report.append(line)
  
  def searchfile(self, fn):
    blok = []
    with open(fn, 'r') as fh:
      for line in fh:
        line=line.rstrip()
        if re.search('^###', line):
          self.searchblok(blok)
          blok = [line, ]
        else:
          blok.append(line)
      self.searchblok(blok)

def parse_arguments():
  parser = argparse.ArgumentParser('note snippets')
  parser.add_argument('-d', '--debug',   action='store_true', help='debug mode')
  parser.add_argument('-l', '--line',    action='store_true', help='show only lines containing the search items')
  parser.add_argument('-s', '--search',  action='append',     help='add one or more search items, all items must be found in a snippet')
  parser.add_argument('-f', '--file',    action='append',     help='add one or more files to note')
  parser.add_argument('--dir', default='/Users/primus/notes', help='note directory path')   # edit this to make it permanent for your environment
  parser.add_argument('-v', '--version', action='version',    version='%(prog)s ' + __version__)
  parser.add_argument('keywords', nargs='*',                  help='create new note with these keywords')
  args = parser.parse_args()
  if not args.keywords and not args.search:
    parser.print_help()
    exit()
  return args

if __name__ == "__main__":
  args = parse_arguments()
  print(notes(args))
