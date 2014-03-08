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
	sizex=len(var)
	if len(noms)==2: sizey=len(var[0])
	for x in range(sizex):
		for y in range(sizey):		
			print var[x][y]['level']
			var[x][y][noms[0]]=x
			if len(noms)==2: var[x][y][noms[1]]=y		


read("/home/horde/.wirechem/dbdata")
print Uworlds
print finished
print len(Uworlds[0])
reference(Uworlds,['world','level'])


