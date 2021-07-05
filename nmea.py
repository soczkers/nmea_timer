#!/usr/bin/env python3

import argparse
import pynmea2
import json
from datetime import datetime, date, timedelta

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
    ise = intersect((prmsg.latitude,prmsg.longitude), (msg.latitude,msg.longitude), (l[0],l[1]), (l[2],l[3]))
    if ise:
        duration = datetime.combine(date.min, msg.timestamp) - datetime.combine(date.min, prmsg.timestamp)
        shift = duration*ise
        return datetime.combine(date.min, prmsg.timestamp) + shift

def previous_name(name, config):
    if name==config["order"][0]:
        return config["order"][-1]
    else:
        return config["order"][config["order"].index(name)-1]
    

parser = argparse.ArgumentParser(description='Script which calucates time between two lines based on NMEA data. There can be multiple intersepcions in one file. Need pynmea2 python library to work. Can be used as post-processing timer for race track. You can check time or whole lap or only specific parts of the track. Script shows the stats')
parser.add_argument('source_file', type=open, help="Source file where are NMEA data(from gps). Need to have there $GPRMC lines")
parser.add_argument('track_file', type=open, help="json file with track")
args = parser.parse_args()
config = json.load(args.track_file)
previous_line=None
p0=None
ises=[]
file = args.source_file
print("checking intersections...")
for line in file.readlines():
    msg = pynmea2.parse(line)
    if msg.sentence_type != "RMC":
        continue
    if not previous_line:
        previous_line=line
        continue
    prmsg=pynmea2.parse(previous_line)
    previous_line=line
    for order in config["order"]:
        Lx=config["line_positions"][order]
        a=ise_point(prmsg,msg,Lx)
        if a:
            ises.append({"name": order, "time": a})
print("ise read complete. Calculating times...")
times=[]
for i, ise in enumerate(ises):
    if i==0:
        continue
    if previous_name(ise["name"],config) == ises[i-1]["name"]:
        times.append({"name": ise["name"], "UTC": ise["time"], "delta": ise["time"]-ises[i-1]["time"]})
    else:
        print("invalid", ise["name"], ise["time"])

best={}
teoretical_best=timedelta(0)
for name in config["order"]:
    for time in times:
        if time["name"]==name:
            if not best.get(name, None) or best[name]["delta"]>time["delta"]:
                best[name]={"name": name, "UTC": time["UTC"], "delta": time["delta"]}
    print(best[name]["name"], best[name]["UTC"], best[name]["delta"])
    teoretical_best+=best[name]["delta"]

print("teoretical best", teoretical_best)
'''
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

'''
