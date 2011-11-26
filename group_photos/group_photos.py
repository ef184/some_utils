#!/usr/bin/python

# max zeitabstand in sekunden
DELTA = 300

import sys
import os
import re
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

def get_exif(fn):
    '''exif-daten zu einer datei fn lesen'''
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def get_date(fn):
    '''DateTimeOriginal aus datei als datetime'''
    info = get_exif(fn)
    d = info['DateTimeOriginal']
    return datetime.strptime(d, '%Y:%m:%d %H:%M:%S')

def build_dict(files):
    '''dict aus zeit und list mit dateinamen'''
    res = {}
    for f in files:    
        d = get_date(f)
        if d not in res:
            res[d] = []
        res[d].append(f)
    return res

def sec_delta(a,b):
    '''abstand zwischen zwei datetimes'''
    td = a - b
    # mit python 2.7 ginge das eleganter:
    return abs((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6 )

def sort_and_group(di):
    '''list mit lists aus files mit zeitabstand <= DELTA'''
    res = []
    dates = sorted(di.keys())
    last_d = dates[0]
    group = []
    group.extend(di[last_d])
    for d in dates[1:]:
        diff = sec_delta(d, last_d)
        if diff > DELTA:    #neue list anfangen, alte ins ergebnis schubsen
            res.append(group)
            group = []
        group.extend(di[d])
        last_d = d
    res.append(group)
    return res

def move_sorted(d, wd):
    '''order fuer jede gruppe von mehr als einem file erstellen und files verschieben, gibt nur shellbefehle aus'''
    num = 1
    for p in d:
        if len(p) > 1:
            foldername = '%s/foo_%05d' % (wd, num)
            num += 1
            print 'mkdir "%s"' % foldername
            for f in p:
                print 'mv "%s" "%s/"' % (f, foldername)
        else:
            print '# ignoring %s' % (p[0])

def list_files(d):
    ''' alle jpgs aus ordner d'''
    return [os.path.join(d, f) for f in os.listdir(d) if  re.match('\.jpe?g$', os.path.splitext(f)[1], re.IGNORECASE ) ]

if __name__ == '__main__':
    working_dir = sys.argv[1].rstrip('/')
    pics = list_files(working_dir)
    picswithdate = build_dict(pics)
    #for a  in sorted(picswithdate.keys()):
    #    print a, picswithdate[a]

    if False:
        picswithdate = {}
        picswithdate[datetime(2010, 1, 1, 2, 3, 4)] = ['a0']
        picswithdate[datetime(2010, 1, 1, 2, 3, 5)] = ['a1']
        picswithdate[datetime(2010, 1, 1, 2, 3, 12)] = ['a2']
        picswithdate[datetime(2010, 1, 1, 2, 3, 12)].append('a3')
        picswithdate[datetime(2010, 1, 1, 2, 3, 13)] = ['a4']
        picswithdate[datetime(2010, 1, 1, 2, 3, 30)] = ['a5']
        picswithdate[datetime(2010, 1, 1, 2, 3, 32)] = ['a6']
    pics_sorted = sort_and_group(picswithdate)
    move_sorted(pics_sorted, working_dir)



