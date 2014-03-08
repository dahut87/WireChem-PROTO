#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import shelve

def read(afile):
	d=shelve.open(afile,writeback=True)
	for k in d.keys():
		globals()[k]=d[k]
	d.close()
	
def load(d):
	for k in d.keys():
		if k[0]!="_":
			globals()[k]=d[k]
		
def reference(var,noms):
	if len(noms)==2: 
		for y in range(len(var)):
			for x in range(len(var[y])):	
				var[y][x][noms[0]]=y
				var[y][x][noms[1]]=x
	else:
		for x in range(len(var[y])):	
			var[x][y][noms[0]]=x	

read("/home/horde/.wirechem/dbdata")
reference(Uworlds,['world','level'])
print Uworlds
print finished
print len(Uworlds[0])



