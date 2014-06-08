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
	global worlds,debug,level
	verifyhome()
	read("dbdata")
	read(gethome()+"/dbdata")
	reference(worlds,['world','level'])
	reference(Uworlds,['world','level'])
	if len(sys.argv)>1 and sys.argv[1]=='debug': 
		debug=1
	else:
		debug=0
		
''' *********************************************************************************************** '''
''' initialisation																		'''
   
debug=0
worlds={}
world=level=0
init()

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
			if self.typeof=='color':
				if not self.isactive():
					color=(self.content[0],self.content[1],self.content[2],127)
				else:
					color=(self.content[0],self.content[1],self.content[2],255)
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
				if not self.isactive():
					self.sprite.color=(60,60,60)
				else:
					self.sprite.color=(255,255,255)
		if type(self.selected) is tuple:
			color=(self.selected[0],self.selected[1],self.selected[2],255)
			self.vertex_list2 = self.window.batch.add(4,pyglet.gl.GL_LINE_LOOP, self.window.p2,
				('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
				('c4B',  color * 4))
		elif type(self.selected) is list and self.isactive():
			self.sprite.color=(self.selected[0],self.selected[1],self.selected[2])
		if self.hilite and int(time.time())%2==0:
			color=(255,0,0,128)
			self.vertex_list3 = self.window.batch.add(4,pyglet.gl.GL_QUADS, self.window.p2,
				('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
				('c4B',  color * 4))		
				
	def __init__(self, window, name, x, y, width, height , active, hilite, visible, selected, content, hint, typeof, text, text2):
		self.name=name
		self.time=0
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
		
	def launch(self,state):
		global debug
		name=self.name.split('_')
		if len(name)>1 and hasattr(self.window, "on_mouse_"+state['event']+"_"+name[0]) and callable(eval("self.window.on_mouse_"+state['event']+"_"+name[0])):
			eval("self.window.on_mouse_"+state['event']+"_"+name[0]+"("+str(name[1])+","+str(state)+")")
			if debug>0: print state,self.name
		if hasattr(self.window, "on_mouse_"+state['event']+"_"+self.name) and callable(eval("self.window.on_mouse_"+state['event']+"_"+self.name)):
			if self.typeof=='multicon':
				self.index+=1
				if self.index>=len(self.content):
					self.index=0
				self.update(0)
			eval("self.window.on_mouse_"+state['event']+"_"+self.name+"("+str(state)+")")
			if debug>0: print state,self.name
		
	def on_mouse_press(self, x, y, button, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			if time.time()-self.time<0.30:
				state={'x':x,'y':y, 'dx':0, 'dy':0, 'buttons':button, 'modifiers':modifiers, 'event': 'double'}
				self.launch(state)			
			self.time=time.time()
			state={'x':x,'y':y, 'dx':0, 'dy':0, 'buttons':button, 'modifiers':modifiers, 'event': 'press'}
			self.launch(state)
				
	def on_mouse_release(self, x, y, button, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():
			state={'x':x,'y':y, 'dx':0, 'dy':0, 'buttons':button, 'modifiers':modifiers, 'event': 'release'}
			self.launch(state)
				
	def on_mouse_drag(self, x, y,  dx, dy, buttons, modifiers):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():	
			state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':buttons, 'modifiers':modifiers, 'event': 'drag'}		
			self.launch(state)
							
	def on_mouse_scroll(self, x, y,  scroll_x, scroll_y):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height and self.isactive() and self.isvisible():	
			state={'x':x,'y':y, 'dx':scroll_x, 'dy':scroll_y, 'buttons':0, 'modifiers':0, 'event': 'scroll'}		
			self.launch(state)
					
	def on_mouse_motion(self, x, y, dx, dy):
		if x>self.x and y>self.y and x<self.x+self.width and y<self.y+self.height:
			if self.isvisible() and self.isactive():
				if self.enter==0:
					self.enter=1
					state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'enter'}
					self.launch(state)
				state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'motion'}
				self.launch(state)
		else:
			if self.enter==1:
				self.enter=0
				state={'x':x,'y':y, 'dx':dx, 'dy':dy, 'buttons':0, 'modifiers':0, 'event': 'leave'}
				self.launch(state)	
					
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
		global debug,worlds,world
		super(menu, self).__init__(width=1024, height=768, resizable=True, fullscreen=False, visible=True, caption="Wirechem: The new chemistry game")
		self.batch = pyglet.graphics.Batch()
		self.p0 = pyglet.graphics.OrderedGroup(0)
		self.p1 = pyglet.graphics.OrderedGroup(1)
		self.p2 = pyglet.graphics.OrderedGroup(2)
		self.p3 = pyglet.graphics.OrderedGroup(3)
		self.p4 = pyglet.graphics.OrderedGroup(4)
		self.clocks=[clock.schedule(self.draw),clock.schedule_interval(self.movefond,0.03)]
		self.loc=[0,0,1,1]
		self.selected=-1
		self.images=[pyglet.image.load('picture/leveler0.png'),pyglet.image.load('picture/leveler1.png'),pyglet.image.load('picture/leveler2.png'),pyglet.image.load('picture/leveler3.png'),pyglet.image.load('picture/leveler4.png')]
		self.colors=[[0,192,244],[235,118,118],[5,157,60],[215,33,255],[201,209,98]]
		#self.fond=pyglet.image.TileableTexture.create_for_image(image.load("picture/fond.png"))
		self.labels=[pyglet.text.Label("",font_name='vademecum',font_size=380,x=0,y=0,bold=False,italic=False,batch=self.batch,group=self.p0,color=(255, 80, 80,230))]
		self.fond=image.load("picture/fond.png")
		self.buttons=[
		abutton(self,'logo',185, self.height-200, 0, 0 , True, False, True, False, pyglet.image.load('picture/logo.png'), 'test', 'icon', '', ''),
		abutton(self,'logo2',45, self.height-150, 0, 0 , True, False, True, False, pyglet.image.load('picture/logo2.png'), 'test', 'icon', '', ''),
		abutton(self,'menu_0',840, 150, 0, 0 , True, False, True, False, pyglet.image.load('picture/arrows.png'), 'test', 'icon', '', ''),
		abutton(self,'menu_1',920, 150, 0, 0 , True, False, True, False, pyglet.image.load('picture/arrows2.png'), 'test', 'icon', '', ''),		
		abutton(self,'menu_2',940, self.height-100, 0, 0 , True, False, True, False, pyglet.image.load('picture/exit2.png'), 'test', 'icon', '', '')
		]
		self.levels=[
		abutton(self,'level_0',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_1',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_2',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_3',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_4',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),		
		abutton(self,'level_5',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_6',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_7',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_8',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_9',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', ''),
		abutton(self,'level_10',-250, 0, 0, 0 , True, False, True, False, self.images[level], 'test', 'icon', '', '')
		]
		self.special=pyglet.sprite.Sprite(pyglet.image.load('picture/boss.png'),batch=self.batch, group=self.p4,x=-150,y=-150)
		self.lock=[pyglet.sprite.Sprite(pyglet.image.load('picture/locked.png'),batch=self.batch, group=self.p4,x=-150,y=-150) for i in range(10)]
		self.untitled=[pyglet.text.Label("",font_name='Vademecum',batch=self.batch, group=self.p4, font_size=23,x=-150,y=-150,bold=False,italic=False,color=(180, 180, 180,255)) for i in range(10)]
		self.untitled2=[pyglet.text.Label("",font_name='Fluoxetine',batch=self.batch, group=self.p4, font_size=18,x=-150,y=-150,bold=False,italic=False,color=(255, 255, 255,255)) for i in range(10)]
		self.update()
		
	def movefond(self,dt):
		global loc
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
		
	def update(self):
		global world,worlds,finished
		for obj in worlds[world]:
			if obj.has_key('special'):
				break
		self.labels[0].text=obj['element']
		self.labels[0].color=(self.colors[world][0],self.colors[world][1],self.colors[world][2],100)
		self.labels[0].x=(1024-self.labels[0].content_width)/2-50
		self.labels[0].y=75*self.height/768
		self.labels[0].text=obj['element']
		for l in range(10):
			if l>=len(worlds[world]):
				self.levels[l].x=-150
				self.untitled[l].x=-150
				self.untitled2[l].x=-150
				self.lock[l].x=-150
				continue
			ele=worlds[world][l]
			self.levels[l].active=(world,l) in finished or debug==2
			self.levels[l].x=ele['_xx']
			self.levels[l].y=ele['_yy']/768.0*self.height
			self.levels[l].setselected([255,120+int(ele['_xx']/1024.0*135),155+int(ele['_xx']/1024.0*100)])
			self.levels[l].content=self.images[world]
			self.levels[l].update(0)
			self.untitled[l].text=ele['element']
			self.untitled[l].x=ele['_xx']+(self.images[world].width-self.untitled[l].content_width)/2
			self.untitled[l].y=ele['_yy']/768.0*self.height+20
			self.untitled[l].color=(int(ele['_xx']/1024.0*150), int(ele['_xx']/1024.0*150), int(ele['_xx']/1024.0*150),255)
			self.untitled2[l].text=ele['nom'].decode('utf-8')
			self.untitled2[l].x=ele['_xx']-(self.untitled2[l].content_width-self.images[world].width)/2
			self.untitled2[l].y=ele['_yy']/768.0*self.height-15
			if (world,l) in finished or debug==2:
				self.untitled2[l].color=(255,255,255,255)
			else:
				self.untitled2[l].color=(90,90,90,255)
			self.lock[l].visible=(world,l) not in finished and not debug==2
			self.lock[l].x=ele['_xx']+10
			self.lock[l].y=ele['_yy']/768.0*self.height+50
			if ele['nom']==obj['nom']:
				self.special.x=ele['_xx']
				self.special.y=ele['_yy']			

	def drawLaser(self,x1,y1,x2,y2,width,power,color,randomize):
		while(width > 0):
			if randomize!=0: glLineStipple(random.randint(0,randomize),random.randint(0,65535))		
			glLineWidth(width)
			glBegin(GL_LINES)
			glColor3ub(min(color[0]+power*width,255),min(color[1]+power*width,255),min(color[2]+power*width,255))
			glVertex2i(x1,y1)
			glVertex2i(x2,y2)
			width=width-1
			glEnd()
			glLineStipple(1,65535)
										
	def draw(self,dt):
		global loc,world,worlds
		glClear(GL_COLOR_BUFFER_BIT);
		#self.fond.anchor_x=self.loc[0]
		#self.fond.anchor_y=self.loc[1]
		glColor4ub(255,255,255,160)
		self.fond.blit(self.loc[0],self.loc[1])
		self.fond.blit(self.loc[0]-1024,self.loc[1])
		self.fond.blit(self.loc[0]-1024,self.loc[1]-768)
		self.fond.blit(self.loc[0],self.loc[1]-768)		
		#self.fond.blit_tiled(0, 0, 0, self.width, self.height)
		'''for ele in worlds[world]:
			for n in ele['link']:
				if n!="" and n[0]==world:
					if n in finished:
						self.drawLaser(ele['_xx']+50,int(ele['_yy']/768.0*self.height+50),worlds[n[0]][n[1]]['_xx']+50,int(worlds[n[0]][n[1]]['_yy']/768.0*self.height+50),random.randint(0,8),20,self.colors[world],12)	
					else:
						self.drawLaser(ele['_xx']+50,int(ele['_yy']/768.0*self.height+50),worlds[n[0]][n[1]]['_xx']+50,int(worlds[n[0]][n[1]]['_yy']/768.0*self.height+50),2,20,[40,40,40],0)		'''
		self.batch.draw()
		
	def on_mouse_press_logo(self, state):
		global debug
		if debug==1:
			debug=2
			self.buttons[0].setselected([255,0,0])			
		elif debug==2:
			debug=1
			self.buttons[0].setselected(False)
		self.update()
		
	def on_mouse_press_menu_2(self, state):
		pyglet.app.exit()
		
	def on_mouse_press_menu_1(self, state):
		global world
		if world>0: world-=1
		self.update()
		
	def on_mouse_press_menu_0(self, state):
		global world
		if world<len(worlds)-1: world+=1
		self.update()
		
	def on_mouse_enter_menu(self, n, state):
		self.buttons[2+n].setselected([255,0,0])
		
	def on_mouse_double_level(self, n, state):
		if debug<2:
			return	
		for ele in worlds[world]:	
			try:
				del ele['special']
			except:
				dummy=0
		worlds[world][n]["special"]=True
		self.update()
		
	def on_mouse_drag_level(self, n, state):
		global worlds,world
		if debug<2:
			return	
		if state['buttons']==2:
			worlds[world][n]["_xx"]+=state['dx']
			worlds[world][n]["_yy"]+=state['dy']
			self.update()
		elif  (state['buttons']==1 or state['buttons']==4) and self.selected==-1:
			self.selected=n
			
	def on_mouse_release_level(self, n, state):
		global worlds,world
		if debug<2:
			return	
		if state['buttons']==1 and self.selected>-1 and n!=self.selected:
			try:
				worlds[world][n]["link"].index((world,self.selected))==-1
			except:
				try: 
					worlds[world][self.selected]["link"].index((world,n))==-1
				except:
					worlds[world][n]["link"].append((world,self.selected))
					self.selected=-1
		elif state['buttons']==4 and self.selected>-1 and n!=self.selected:
			try:
				worlds[world][n]["link"].remove((world,self.selected))
			except:
				dummy=0
			try:
				worlds[world][self.selected]["link"].remove((world,n))
			except:
				dummy=0
		else:
			self.selected=-1
			
	def on_mouse_leave_menu(self, n, state):
		self.buttons[2+n].setselected(False)
		
	def on_mouse_enter_level(self, n, state):
		global world
		self.levels[n].setselected([255,0,0])
		self.untitled2[n].color=(255,0,0,255)
		
	def on_mouse_leave_level(self, n, state):
		self.levels[n].setselected([255,120+int(self.levels[n].x/1024.0*135),155+int(self.levels[n].x/1024.0*100)])
		self.untitled2[n].color=(255,255,255,255)

	def on_mouse_press_level(self, n, state):
		if debug==2:
			self.selected=-1
			if state['modifiers']==17:
				del worlds[world][n]
				self.update()
			return	
		
	def on_mouse_press(self, x, y, button, modifiers):
		if debug<2:
			return		
		if modifiers==18 and len(worlds[world])<10:
			worlds[world].append({'nom': 'nouveau',
  'description': "niveau tout neuf.",
  'element': 'x',
  'current': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  'victory': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  'cout': 0,
  'tech': 0,
  'cycle': 0,  
  'maxcycle': 99999,     
  'nrj': 0,   
  'maxnrj': 99999, 
  'rayon': 0,  
  'maxrayon': 99999,   
  'temp': 0,     
  'maxtemp': 99999,
  '_xx': x,
  '_yy': y,
  'link': [],
  'video': False,
  'special': False,
  'world_art': [[0,0,0],[0,0,0],[0,0,0]],
  'world_new': [[0,0,0],[0,0,0],[0,0,0]]})
			self.update()
  
  
''' *********************************************************************************************** '''
''' Lancement du menu principal																					'''

pyglet.font.add_file('font/Fluoxetine.ttf')
pyglet.font.add_file('font/OpenDyslexicAlta.otf')
pyglet.font.add_file('font/Mecanihan.ttf')
pyglet.font.add_file('font/Vademecum.ttf')
pyglet.font.add_file('font/LiberationMono-Regular.ttf')
menu_principal = menu()
menu_principal.set_minimum_size(1024, 768)
glEnable(GL_BLEND);
glEnable(GL_STENCIL_TEST);
glEnable(GL_LINE_SMOOTH);
glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST);
glEnable(GL_LINE_STIPPLE)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
pyglet.app.run()   
        
        
        
        
        


