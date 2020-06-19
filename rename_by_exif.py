#!/usr/bin/env python3
'''
Rename photo files in a directory with year and follow number
Format yyyy-nnnn.<ext>
Use exifread to number the photos in correct date order

20200617  1.2  primus  converted to class
20190323  1.1  primus  changed path and converted file extension to lowercase
20161106  1.0  primus  fixed a bug if same follow number exists
20160331  0.1  primus  translated from my good old perl script
'''

import os, re
import shutil
import datetime
import exifread

class renumber_photo_files(object):

  def __init__(self, path='.', year=datetime.datetime.now().strftime("%Y"), last='1000'):
    self.path  = path
    self.last  = last
    self.year  = year
    self.exts  = r'\.(jpg|JPG|cr2|CR2)$'
    self.rlist = []
    self.make_list()
    self.report()
    self.rename_files()

  def make_list(self):
    for dir, subdir, fl in os.walk(self.path):
      for fname in fl:
        ft = re.search(self.exts, fname)
        if not ft:         # check extension
          continue
        m=re.search('^'+self.year+r'-(\d{4})'+self.exts, fname)
        if m:                                                # is filename already in correct format?
          if int(m.group(1)) > int(self.last):               # then look for the highest number
            self.last = m.group(1)
        else:
          stamp='???'
          with open(os.path.join(dir, fname), 'rb') as f:     # otherwise try to find an exif timestamp
            tags = exifread.process_file(f, stop_tag='DateTimeOriginal')
            if 'EXIF DateTimeOriginal' in tags.keys():
              stamp=str(tags['EXIF DateTimeOriginal'])
          self.rlist.append((stamp, dir, fname, ft.group(1))) # keep a list of usefull items
  
  def __iter__(self):
    ml=self.last
    for fn in sorted(self.rlist):   
      ml='{}'.format(str(int(ml)+1))
      yield os.path.join(fn[1],fn[2]), os.path.join(fn[1], '{}-{}.{}'.format(self.year, ml, fn[3].lower()))
  
  def report(self):
    print('check it: last =',self.last)
    for f1, f2 in self.__iter__():
      print('mv', f1, f2)
  
  def rename_files(self):
    n = len(list(self.__iter__()))
    if n > 0:
      if re.search(r'y|yes',input(f'Are you sure to rename {n} files ? ').lower()): 
        for f1, f2 in self.__iter__():
          shutil.move(f1, f2)
        print('done')
      else:
        print('aborted')      

if __name__ == '__main__':
  renumber_photo_files(path='/Users/primus/photos')
