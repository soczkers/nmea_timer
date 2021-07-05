#!/usr/bin/env python3

import argparse
import pynmea2
from datetime import datetime, date

def intersect(p1, p2, p3, p4):
    x1,y1 = p1
    x2,y2 = p2
    x3,y3 = p3
    x4,y4 = p4
    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom == 0: # parallel
        return None
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    if ua < 0 or ua > 1: # out of range
        return None
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    if ub < 0 or ub > 1: # out of range
        return None
    return ua

def ise_point(prmsg, msg, l):
    ise = intersect((prmsg.latitude,prmsg.longitude), (msg.latitude,msg.longitude), l[0],l[1])
    if ise:
        duration = datetime.combine(date.min, msg.timestamp) - datetime.combine(date.min, prmsg.timestamp)
        shift = duration*ise
        return datetime.combine(date.min, prmsg.timestamp) + shift



parser = argparse.ArgumentParser(description='Script which calucates time between two lines based on NMEA data. There can be multiple intersepcions in one file. Need pynmea2 python library to work. Can be used as post-processing timer for race track. You can check time or whole lap or only specific parts of the track. Script shows the stats')
parser.add_argument('source_file', type=open, help="Source file where are NMEA data(from gps). Need to have there $GPRMC lines")
parser.add_argument('LOOlat', type=float, help="First line (start) first point latitiude")
parser.add_argument('LOOlon', type=float, help="First line (start) first point longitude")
parser.add_argument('LO1lat', type=float, help="First line (start) second point latitiude")
parser.add_argument('LO1lon', type=float, help="First line (start) second point longitude")
parser.add_argument('L1Olat', type=float, help="Second line (finish) first point latitiude")
parser.add_argument('L1Olon', type=float, help="Second line (finish) first point longitude")
parser.add_argument('L11lat', type=float, help="Second line (finish) second point latitiude")
parser.add_argument('L11lon', type=float, help="Second line (finish) second point longitude")
args = parser.parse_args()
L0=(args.LOOlat, args.LOOlon), (args.LO1lat, args.LO1lon)
L1=(args.L1Olat, args.L1Olon), (args.L11lat, args.L11lon)
previous_line=None
p0=None
times=[]
hours=[]
file = args.source_file
for line in file.readlines():
    msg = pynmea2.parse(line)
    if msg.sentence_type != "RMC":
        continue
    if not previous_line:
        previous_line=line
        continue
    prmsg=pynmea2.parse(previous_line)
    previous_line=line
    a=ise_point(prmsg,msg,L1)
    if a and p0:
        times.append(a-p0)
        hours.append(a)
        p0=None
    b=ise_point(prmsg,msg,L0)
    if b: 
        p0=b

for i,a in enumerate(times):
    print (i, a, hours[i])
print ("min:", times.index(min(times)), min(times), hours[times.index(min(times))])
print ("max:", times.index(max(times)), max(times))
