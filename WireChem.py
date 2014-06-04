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
		
class abutton(object):
	def update(self):
		if not self.isvisible():
			try:
				self.vertex_list.delete()
			except:
				print "destroyed"
		else:
			if self.typeof=='icon':
				self.content.width=self.width
				self.content.height=self.height				
				self.vertex_list = pyglet.sprite.Sprite(self.content, x=self.x, y=self.y, batch=self.batch)
			elif self.typeof=='color':
				self.vertex_list = self.batch.add(4,pyglet.gl.GL_QUADS, None,
                                          ('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
                                          ('c4B', self.content * 4))
			elif self.typeof=='function':
				self.vertex_list = eval(self.content)
			elif self.typeof=='multicon':
				self.content[self.index].width=self.width
				self.content[self.index].height=self.height	
				self.vertex_list = pyglet.sprite.Sprite(self.content[self.index], x=self.x, y=self.y, batch=self.batch)
				
	def __init__(self, window, name, x, y, width, height , active, hilite, visible, seleted, separe, content, hint, typeof, text, text2, batch):
		self.name=name
		self.index=0
		self.x=x
		self.y=y
		self.batch=batch
		self.width=width
		self.height=height
		self.active=active
		self.hilite=hilite
		self.visible=visible
		self.separe=separe
		self.content=content
		self.typeof=typeof
		self.hint=hint
		self.seleted=seleted
		self.window=window
		self.window.push_handlers(self.on_mouse_press)
		self.window.push_handlers(self.on_mouse_motion)
		self.window.push_handlers(self.on_mouse_drag)
		self.window.push_handlers(self.on_mouse_release)
		self.window.push_handlers(self.on_mouse_scroll)		
		self.update()
		
	def delete(self):
		self.vertex_list.delete()
		
	def on_mouse_press(self, x, y, button, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			if hasattr(self.window, "on_mouse_press_"+self.name) and callable(eval("self.window.on_mouse_press_"+self.name)):		
				state={'x':x,'y':y, 'dx':0, 'dy':0, 'buttons':button, 'modifiers':modifiers, 'event': 'press'}	
				if self.typeof=='multicon':
					self.index+=1
					if self.index>=len(self.content):
						self.index=0
					self.update()
				eval("self.window.on_mouse_press_"+self.name+"("+str(state)+")")
				
	def on_mouse_release(self, x, y, button, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			if hasattr(self.window, "on_mouse_release_"+self.name) and callable(eval("self.window.on_mouse_release_"+self.name)):		
				state={'x':x,'y':y, 'dx':0, 'dy':0, 'buttons':button, 'modifiers':modifiers, 'event': 'release'}		
				eval("self.window.on_mouse_release_"+self.name+"("+str(state)+")")
				
	def on_mouse_drag(self, x, y,  dx, dy, buttons, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			if hasattr(self.window, "on_mouse_drag_"+self.name) and callable(eval("self.window.on_mouse_drag_"+self.name)):		
				state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':buttons, 'modifiers':modifiers, 'event': 'drag'}		
				eval("self.window.on_mouse_drag_"+self.name+"("+str(state)+")")
			
	def on_mouse_scroll(self, x, y,  scroll_x, scroll_y):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			if hasattr(self.window, "on_mouse_scroll_"+self.name) and callable(eval("self.window.on_mouse_scroll_"+self.name)):		
				state={'x':x,'y':y, 'dx':scroll_x, 'dy':scroll_y, 'buttons':0, 'modifiers':0, 'event': 'scroll'}		
				eval("self.window.on_mouse_scroll_"+self.name+"("+str(state)+")")
	
	def on_mouse_motion(self, x, y, dx, dy):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible(): 
			if hasattr(self.window, "on_mouse_motion_"+self.name) and callable(eval("self.window.on_mouse_motion_"+self.name)):
				state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'motion'}	
				eval("self.window.on_mouse_motion_"+self.name+"("+str(state)+")")
				
	def isvisible(self):
		if type(self.visible) is bool:
			return self.visible
		else:
			return eval(self.visible)
			
	def isactive(self):
		if type(self.active) is bool:
			return self.active
		else:
			return eval(self.active)
			
	def ishilite(self):
		if type(self.hilite) is bool:
			return self.hilite
		else:
			return eval(self.hilite)	
	
	def hide(self):
		if type(self.visible) is bool:
			self.visible=False
			self.update()
		
	def show(self):
		if type(self.visible) is bool:
			self.visible=True
			self.update()
	
	def activate(self):
		if type(self.active) is bool:
			self.active=True
			self.update()
	
	def unactivate(self):
		if type(self.active) is bool:
			self.active=False
			self.update()
	
	def hilite(self):
		if type(self.hilite) is bool:
			self.hilite=True
			self.update()
	
	def unhilite(self):
		if type(self.hilite) is bool:
			self.hilite=False
			self.update()


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
		self.buttons=[abutton(self,'test',10, 10, 50, 50 , True, True, True, False, False, (255,0,0,255), 'test', 'color', '', '', self.batch),abutton(self,'prout',150, 150, 150, 50 , True, True, True, False, False, (0,255,0,255), 'test', 'color', '', '', self.batch),abutton(self,'aicon',70, 70, 150, 100 , True, True, True, False, False, [pyglet.image.load('picture/boss.png'),pyglet.image.load('picture/exits.png')], 'test', 'multicon', '', '', self.batch)]
        
	def draw(self,dt):
		glClearColor(0,0,0,255)
		self.clear()
		self.batch.draw()
		
	def on_mouse_press_test(self, state):
		print "test est appuyé"
		if self.buttons[0].isvisible():
			self.buttons[0].hide()
		else:
			self.buttons[0].show()
		
	def on_mouse_motion_test(self, state):
		print "test est motion en "+str(state['x'])

	def on_mouse_press_prout(self, state):
		self.buttons[0].unactivate()
	
	def on_mouse_motion_prout(self, state):
		print "prout "+str(state['x'])
		
	def on_mouse_scroll_aicon(self, state):
		print "essai "+str(state['dy'])
	
	def on_mouse_press_aicon(self, state):
		print "essai "+str(state['dy'])
        
''' *********************************************************************************************** '''
''' Initialisation																					'''
     
glEnable(GL_BLEND);
'''glEnable(GL_LINE_SMOOTH);
glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST);'''
glEnable(GL_LINE_STIPPLE)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
menu_principal = menu()
pyglet.app.run()   
        
        
        
        
        


