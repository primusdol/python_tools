#!/usr/bin/env python3
'''
note.py            add note snippets to a file
note.py -g regexp  grep items from the saved snippets


20201213 1.9  primus  with option to attach files to notes
20201209 1.8  primus  rewritten as class
20180918 1.7  primus  replace non ascii chars with "~"
20161129 1.4  primus  split db file per year
20150722 1.1  primus  argv argumenten included
20150715 1.0  primus  port from perl
'''
__version__ = '1.9'

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
    self.dir = os.path.join('/Users/primus/notes')  # directory with note files
    self.check_dir(self.dir)
    self.db  = os.path.join(self.dir, 'notes{}.db'.format(self.year))    # current note file
    self.filestore = os.path.join(self.dir, 'notes{}'.format(self.year)) # path to store appended files
    self.check_dir(self.filestore)
    for db in os.listdir(self.dir):
      if re.search ('notes[0-9]{4}.db', db):
        self.files.append(os.path.join(self.dir, db))
    if self.args.search != '':   # search in notes
      for fn in self.files:
        self.grepnote(fn) 
    else:                      # add new note
      self.newnote()

  def add_report(self, h, b):
     self.report.append(h)
     self.report.append(b)
     
  def check_dir(self, path):
    '''
    check if the directory exists otherwise create it
    '''
    if not os.path.exists(path):
      try:
        os.mkdir(path)
      except OSError as e:
        logging.error('mkdir {} failed: {}'.format(path, e))

  def __repr__(self):
     return ''.join(map(str,self.report))
  
  def newnote(self):
    hdr = '### {} {}'.format(self.stamp, ' '.join(map(str, self.args.argv)))
    print('keywords {}'.format(' '.join(map(str, self.args.argv))))
    print('enter text for the new note, end with met ctrl-z or ctrl-d')
    with open(self.db, 'a') as fh:
      fh.write('\n{}\n'.format(hdr))
      for line in sys.stdin:
        line=re.sub(r'[^\x09-\x7e]','~',line)  # strip all kind of junk
        fh.write(line)
      if self.args.file:
        for i, fn in enumerate (self.args.file):
          if os.path.exists(fn):
            fs = '{}-{:02d}{}'.format(self.stamp, i+1, pathlib.Path(fn).suffix.lower())
            fh.write('\n{{{{ {} }}}}'.format(fs))
            shutil.copy(fn, os.path.join(self.filestore, fs))
          else:
            logging.error('file {} not found'.format(fn)) 

  def grepnote(self, fn):
    try:
      blok, header, found = '', '', False
      with open(fn, 'r') as fh:
        for line in fh:
          newblok = re.search('^###', line)
          in_line = re.search(self.args.search, line, re.IGNORECASE)
          if newblok:
            if found:
              self.add_report(header, blok)
            blok, header, found = '', line, False
          if in_line:
            found = True
          if (not newblok and ((self.args.line and in_line) or (not self.args.line))):
            blok += line
      if found:
        self.add_report(header, blok)
    except Exception as e:
      logging.error('{}'.format(e))

def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--debug',     action='store_true')
  parser.add_argument('-l', '--line',      action='store_true',  help='show only lines containing the search items')
  parser.add_argument('-s', '--search',    type=str, default='', help='regular expression to search in notes')
  parser.add_argument('-f', '--file',      action='append',      help='add one or more files to note')
  parser.add_argument('-v', '--version',   action='version', version='%(prog)s ' + __version__)
  parser.add_argument('argv', nargs='*')
  args = parser.parse_args()
  return args

if __name__ == "__main__":
  args = parse_arguments()
  print(notes(args))
