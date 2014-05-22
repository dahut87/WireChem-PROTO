#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
  ------------------------------------------
  
  WireChem - The new chemistry game
  
  Programme principal

  (C) Copyright 2013-2014 Nicolas Hordé
  Licence GPL V3.0
  
  ------------------------------------------
'''
import datetime
import math
import pyglet
import copy
import csv
import random
import time
import operator
import shelve
import os
import sys
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from pyglet import clock
from pyglet import image
from os.path import expanduser
	
''' *********************************************************************************************** '''
''' Fonctions d'initialisation																							 '''

def sync():
	global Uworlds,finished
	write(gethome()+"/dbdata",["Uworlds","finished"])

def verifyhome():
	global Uworlds,finished
	if not os.path.exists(gethome()):
		os.makedirs(gethome())
	if not os.path.exists(gethome()+"/dbdata"):
		Uworlds=[[{0:0}]]
		finished=[(0,0)]
		sync()
	
def gethome():
	home = expanduser("~")+"/.wirechem"
	return home

def write(afile,var):
	d=shelve.open(afile,writeback=True)
	for k in var:
		d[k]=copy.deepcopy(globals()[k])
	d.sync()
	d.close()	

def read(afile):
	d=shelve.open(afile,writeback=True)
	for k in d.keys():
		globals()[k]=copy.deepcopy(d[k])
	d.close()
	
def load(d):
	for k in d.keys():
		if k[0]!="_":
			globals()[k]=copy.deepcopy(d[k])
		
def reference(var,noms):
	if len(noms)==2: 
		for y in range(len(var)):
			for x in range(len(var[y])):	
				var[y][x][noms[0]]=y
				var[y][x][noms[1]]=x
	else:
		for x in range(len(var[y])):	
			var[x][y][noms[0]]=x	
			
def duplicateref(d):
	for k in d.keys():
		d[d[k]['nom']]=d[k]

''' *********************************************************************************************** '''
''' Gestion du plateau de jeu																						 '''
				
class game(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(game, self).__init__(resizable=True, fullscreen=False, visible=True, caption="Wirechem: The new chemistry game")
		self.batch = pyglet.graphics.Batch()
		self.clocks=[clock.schedule(self.draw)]
		self.labels = []
        
	def draw(self,dt):
		glClearColor(0,0,0,255)
		self.clear()
		
''' *********************************************************************************************** '''
''' Gestion du menu principal																						 '''
				
class menu(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(menu, self).__init__(resizable=True, fullscreen=False, visible=True, caption="Wirechem: The new chemistry game")
		self.batch = pyglet.graphics.Batch()
		self.clocks=[clock.schedule(self.draw)]

        
	def draw(self,dt):
		glClearColor(0,0,0,255)
		self.clear()
		self.batch.draw()
        
''' *********************************************************************************************** '''
''' Initialisation																					'''
     
glEnable(GL_BLEND);
'''glEnable(GL_LINE_SMOOTH);
glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST);'''
glEnable(GL_LINE_STIPPLE)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
menu_principal = menu(resizable=True)
pyglet.app.run()   
        
        
        
        
        


