#!/usr/bin/env python3
'''
Store all your text snippets to a file.
Use keywords to find your snippets easily back
I use it to store all kind of coding fragments.
But also for installation instructions, and even for cooking recepts and all kind of things I always forget
You can also edit the notefile with your favorite editor 

note.py  keyword [keyword] ..         add note snippets to a file
note.py -s searchstring               search items from the saved snippets

You can edit the '--file' argument to your preferred file location and name

20250314 2.3  primus  cleaned up
20250314 2.2  primus  simplified to 1 file system
20230412 2.1  primus  strip all non printable characters
20201221 2.0  primus  now with multiple search items
20150722 1.1  primus  keyword argumenten included
20150715 1.0  primus  port from perl
'''
__version__ = '2.2'

import re, os, sys
import datetime
import argparse
import string

  
def newnote(args):
  header = f'### {datetime.datetime.now().strftime("%Y%m%d-%H%M")} {' '.join(map(str, args.keywords))}'
  print('enter text for the new note, end with met ctrl-z or ctrl-d')
  with open(args.file, 'a') as fh:
    fh.write(f'\n{header}\n')
    for line in sys.stdin:
      line = ''.join(filter(lambda x: x in set(string.printable), line))
      fh.write(line)

def searchsnippet(args, snippet):
  hit = []
  line_cnt = [0, ]
  for j, s in enumerate(args.search):
    hit.append(False)
    for i ,line in enumerate(snippet):
      if re.search(s, line, re.I):   # ignore case
        hit[j] = True
        line_cnt.append(i)
  for h in hit:
    if not h:  # block must contain all search items
      return
  for i ,line in enumerate(snippet):
    if i in line_cnt or not args.line: # report line if it contains any of the search items or is the first line
       print(line)

def searchfile(args):
  snippet = []
  cnt = 0
  with open(args.file, 'rb') as fh:
    for line in fh:
      cnt += 1
      try:
        line = line.decode('utf-8', 'replace')
        line = line.rstrip()
        line = ''.join(filter(lambda x: x in set(string.printable), line))
      except Exception as e:
        line = f'problem decoding to utf-8 in file {args.file} line {cnt}'
        print(line)
      if re.search('^### [0-9]{6}', line):
        searchsnippet(args, snippet)
        snippet = [line, ]
      else:
        snippet.append(line)
  searchsnippet(args, snippet)  


if __name__ == '__main__':
  parser = argparse.ArgumentParser('note snippets')
  parser.add_argument('-l', '--line',    action='store_true',   help='show only lines containing the search items')
  parser.add_argument('-s', '--search',  action='append',       help='add one or more search items, all items must be found in a snippet')
  parser.add_argument('-f', '--file',    type=str, default='notes.txt', help='file to store the snippets, change this to your preferred file location')  
  parser.add_argument('-v', '--version', action='version',      version='%(prog)s ' + __version__)
  parser.add_argument('keywords', nargs='*',                    help='create new note with these keywords')
  args = parser.parse_args()
  
  if not args.keywords and not args.search:
    parser.print_help()
    exit()

  if not os.path.isfile(args.file):
    if not input(f'file {args.file} does not exist, start with an empty file (Y/N)').lower() in ('yes','y','ja','j'):
      exit()

  if args.search:                      # search in notes
    args.search.extend(args.keywords)  # extend all unspecified keyword arguments to the search items, all must be found in the snipped
    searchfile(args) 
  else:                                # add new note
    newnote(args)

