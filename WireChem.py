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
''' Fonctions de chargement  																		'''

#Enregistre les données utilisateurs
def sync():
	global Uworlds,finished
	write(gethome()+"/dbdata",["Uworlds","finished"])

#Vérifie l'existence de la base de donnée utilisateur
def verifyhome():
	global Uworlds,finished
	if not os.path.exists(gethome()):
		os.makedirs(gethome())
	if not os.path.exists(gethome()+"/dbdata"):
		Uworlds=[[{0:0}]]
		finished=[(0,0)]
		sync()

#Trouve le chemin vers le repertoire utilisateur	
def gethome():
	home = expanduser("~")+"/.wirechem"
	return home

#Ecrit les variables spécifiés dans la base selectionnée (utilisateur ou système)
def write(afile,var):
	d=shelve.open(afile,writeback=True)
	for k in var:
		d[k]=copy.deepcopy(globals()[k])
	d.sync()
	d.close()	

#Lit une base de donnée
def read(afile):
	d=shelve.open(afile,writeback=True)
	for k in d.keys():
		globals()[k]=copy.deepcopy(d[k])
	d.close()
	
#Charge le dictionnaire sous forme de variables
def load(d):
	for k in d.keys():
		if k[0]!="_":
			globals()[k]=copy.deepcopy(d[k])
		
#Référence les variables
def reference(var,noms):
	if len(noms)==2: 
		for y in range(len(var)):
			for x in range(len(var[y])):	
				var[y][x][noms[0]]=y
				var[y][x][noms[1]]=x
	else:
		for x in range(len(var[y])):	
			var[x][y][noms[0]]=x	
			
#duplique les références
def duplicateref(d):
	for k in d.keys():
		d[d[k]['nom']]=d[k]
		
		
''' *********************************************************************************************** '''
''' Sauvegarde/Restauration '''

def readlevel(w,l,user):
	global tuto,worlds,cout,selected,sizex,sizey,stat,tech
	tuto=''
	if user:
		if w<len(Uworlds) and l<len(Uworlds[w]) and Uworlds[w][l].has_key("element"):
			load(Uworlds[w][l])
		else:
			load(worlds[w][l])
	else:
		load(worlds[w][l])
	menus[0][18]['icon']=copy.deepcopy(art['null'])
	sizex=len(world_new)
	sizey=len(world_new[0])
	resize();	
	stat=[0,0,0,0,0,0,0,0,0]
	over=0
	infos()

def savelevel(w,l):
	global tuto,users,worlds,Uworlds,nom,descriptif,video,link,tech,cout,victory,current,cycle,nrj,rayon,temp,maxcycle,maxnrj,maxrayon,maxtemp,world_new,world_art
	while len(Uworlds)<=w:
		Uworlds.append(0)
		Uworlds[w]=[]
	while len(Uworlds[w])<=l:
		Uworlds[w].append({})
		Uworlds[w][l]={'nom':nom,
'element':element,
'users':users,
'tuto':tuto,
'description':descriptif,
'_xx':worlds[world][level]['_xx'],
'_yy':worlds[world][level]['_yy'],
'video':video,
'link':link,
'level':level,
'world':world,
'tech':tech,
'cout':cout,
'victory':victory,
'current':worlds[world][level]['current'],
'cycle':cycle,
'nrj':nrj,
'rayon':rayon,
'temp':temp,
'maxcycle':maxcycle,
'maxnrj':maxnrj,
'maxrayon':maxrayon,
'maxtemp':maxtemp,
'world_new':world_new,
'world_art':world_art}
		
''' *********************************************************************************************** '''
''' Fonction d'initialisation  																				'''

#initialisation du jeu
def init():
	global worlds,debug
	verifyhome()
	read("dbdata")
	read(gethome()+"/dbdata")
	reference(worlds,['world','level'])
	reference(Uworlds,['world','level'])
	if len(sys.argv)>1 and sys.argv[1]=='debug': 
		debug=True
	else:
		debug=False
		
''' *********************************************************************************************** '''
''' initialisation																		'''
   
debug=False
worlds={}
init()
print debug

''' *********************************************************************************************** '''
''' Classes graphiques																		'''

#Bouton sensible a plusieurs évènements
class abutton(object):
	def update(self,dt):
		try:
			self.vertex_list.delete()
		except:
			foo=0
		try:
			self.vertex_list2.delete()
		except:
			foo=0
		try:
			self.vertex_list3.delete()
		except:
			foo=0
		try:
			self.sprite.delete()
		except:
			foo=0		
		if self.isvisible():
			if not self.isactive():
				color=127
			else:
				color=255
			if self.typeof=='color':
				color=(self.content[0],self.content[1],self.content[2],color)
				self.vertex_list = self.window.batch.add(4,pyglet.gl.GL_QUADS, self.window.p1,
                                          ('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
                                          ('c4B',  color * 4))
			elif self.typeof=='function':
				self.vertex_list = eval(self.content)
			else:
				if self.typeof=='multicon':
					image = self.content[self.index]
				else:
					image = self.content
				if self.width==0 or self.height==0:
					self.width=image.width
					self.height=image.height
				self.sprite = pyglet.sprite.Sprite(image, x=self.x, y=self.y, batch=self.window.batch, group=self.window.p1)
				if self.width/float(self.height) < image.width/float(image.height):
					self.sprite.scale=float(self.width)/image.width
				else:
					self.sprite.scale=float(self.height)/image.height
				self.sprite.opacity=color
		if type(self.selected) is tuple:
			color=(self.selected[0],self.selected[1],self.selected[2],255)
			self.vertex_list2 = self.window.batch.add(4,pyglet.gl.GL_LINE_LOOP, self.window.p2,
				('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
				('c4B',  color * 4))
		elif type(self.selected) is list:
			self.sprite.color=(self.selected[0],self.selected[1],self.selected[2])
		if self.hilite and int(time.time())%2==0:
			color=(255,0,0,128)
			self.vertex_list3 = self.window.batch.add(4,pyglet.gl.GL_QUADS, self.window.p2,
				('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
				('c4B',  color * 4))		
				
	def __init__(self, window, name, x, y, width, height , active, hilite, visible, selected, content, hint, typeof, text, text2):
		self.name=name
		self.index=0
		self.enter=0
		self.x=x
		self.y=y
		self.width=width
		self.height=height
		self.active=active
		self.hilite=hilite
		self.visible=visible
		self.content=content
		self.typeof=typeof
		self.hint=hint
		self.selected=selected
		self.window=window
		self.window.push_handlers(self.on_mouse_press)
		self.window.push_handlers(self.on_mouse_motion)
		self.window.push_handlers(self.on_mouse_drag)
		self.window.push_handlers(self.on_mouse_release)
		self.window.push_handlers(self.on_mouse_scroll)	
		self.updateclock=clock.schedule_interval(self.update,1)	
		self.update(0)
		
	def delete(self):
		self.vertex_list.delete()
		del self
		self=None
		
	def on_mouse_press(self, x, y, button, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			if hasattr(self.window, "on_mouse_press_"+self.name) and callable(eval("self.window.on_mouse_press_"+self.name)):		
				state={'x':x,'y':y, 'dx':0, 'dy':0, 'buttons':button, 'modifiers':modifiers, 'event': 'press'}	
				if self.typeof=='multicon':
					self.index+=1
					if self.index>=len(self.content):
						self.index=0
					self.update(0)
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
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height:
			if self.isvisible() and self.isactive():
				if self.enter==0:
					self.enter=1
					if hasattr(self.window, "on_mouse_enter_"+self.name) and callable(eval("self.window.on_mouse_enter_"+self.name)):
						state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'enter'}
						eval("self.window.on_mouse_enter_"+self.name+"("+str(state)+")")
				if hasattr(self.window, "on_mouse_motion_"+self.name) and callable(eval("self.window.on_mouse_motion_"+self.name)):	
					state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'motion'}
					eval("self.window.on_mouse_motion_"+self.name+"("+str(state)+")")
		else:
			if self.enter==1:
				self.enter=0
				state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'leave'}
				if hasattr(self.window, "on_mouse_leave_"+self.name) and callable(eval("self.window.on_mouse_leave_"+self.name)):	
					eval("self.window.on_mouse_leave_"+self.name+"("+str(state)+")")	
					
	def setselected(self,select):
		self.selected=select
		self.update(0)					
				
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
			self.update(0)
		
	def show(self):
		if type(self.visible) is bool:
			self.visible=True
			self.update(0)
	
	def activate(self):
		if type(self.active) is bool:
			self.active=True
			self.update(0)
	
	def unactivate(self):
		if type(self.active) is bool:
			self.active=False
			self.update(0)
	
	def hilitate(self):
		if type(self.hilite) is bool:
			self.hilite=True
			self.update(0)
	
	def unhilitate(self):
		if type(self.hilite) is bool:
			self.hilite=False
			self.update(0)


''' *********************************************************************************************** '''
''' Gestion du plateau de jeu																						 '''
				
#Classe du plateau de jeu
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
				
#Classe du menu principal
class menu(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		global debug,worlds
		super(menu, self).__init__(width=1024, height=768, resizable=True, fullscreen=False, visible=True, caption="Wirechem: The new chemistry game")
		self.batch = pyglet.graphics.Batch()
		self.p0 = pyglet.graphics.OrderedGroup(0)
		self.p1 = pyglet.graphics.OrderedGroup(1)
		self.p2 = pyglet.graphics.OrderedGroup(2)
		self.p3 = pyglet.graphics.OrderedGroup(3)
		self.clocks=[clock.schedule(self.draw)]
		self.loc=[0,0,1,1]
		self.fond=pyglet.image.TileableTexture.create_for_image(image.load("picture/fond.png"))
		self.buttons=[abutton(self,'logo',185, self.height-200, 0, 0 , True, False, True, False, pyglet.image.load('picture/logo.png'), 'test', 'icon', '', ''),
		abutton(self,'logo2',45, self.height-150, 0, 0 , True, False, True, False, pyglet.image.load('picture/logo2.png'), 'test', 'icon', '', ''),
		abutton(self,'arrows',840, 150, 0, 0 , True, False, True, False, pyglet.image.load('picture/arrows.png'), 'test', 'icon', '', ''),
		abutton(self,'arrows2',920, 150, 0, 0 , True, False, True, False, pyglet.image.load('picture/arrows2.png'), 'test', 'icon', '', ''),		
		abutton(self,'exit2',940, self.height-100, 0, 0 , True, False, True, False, pyglet.image.load('picture/exit2.png'), 'test', 'icon', '', '')]
		
        
	def draw(self,dt):
		glClearColor(0,0,0,255)
		self.clear()
		self.loc[0]+=self.loc[2]
		self.loc[1]+=self.loc[3]
		if self.loc[0]>1024:
			self.loc[2]=-1
		if self.loc[1]>768:
			self.loc[3]=-1
		if self.loc[0]<0:
			self.loc[2]=1
		if self.loc[1]<0:
			self.loc[3]=1
		self.fond.blit_tiled(0, 0, 0, self.width, self.height)
		self.batch.draw()
		
	def on_mouse_press_exit2(self, state):
		pyglet.app.exit()
		
	def on_mouse_enter_exit2(self, state):
		self.buttons[4].setselected([255,0,0])
		
	def on_mouse_leave_exit2(self, state):
		self.buttons[4].setselected(False)
		
''' *********************************************************************************************** '''
''' Lancement du menu principal																					'''
   
menu_principal = menu()
menu_principal.set_minimum_size(1024, 768)
glEnable(GL_BLEND);
glEnable(GL_LINE_SMOOTH);
glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST);
glEnable(GL_LINE_STIPPLE)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
pyglet.app.run()   
        
        
        
        
        


