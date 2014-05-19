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

''' ************************************************************************************************ '''
''' Initialisation & Chargement																		 '''

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
				
def loadpic(d):
	for j in range(len(d)):
		for k in range(len(d[j])):
			if 'icon' in d[j][k]:
				if type(d[j][k]['icon']) is str and d[j][k]['icon']!="" and os.path.exists(d[j][k]['icon']):
					d[j][k]['icon']=image.load(d[j][k]['icon'])
				elif type(d[j][k]['icon']) is list and type(d[j][k]['icon'][0]) is str:
					for n in range(len(d[j][k]['icon'])):
						d[j][k]['icon'][n]=image.load(d[j][k]['icon'][n])					
									
def initgrid():
	global loc,msg,rect,tuto,savenames,menus,users,art,Uworlds,statedvar,stat_var,seestat,adirection,worlds,finished,allcout,selected,world,level,over,sizex,sizey,world_old,world_new,world_art,dat,direction,zoom,play,stat,cycle,cout,thecout,rayon,debug,temp,decx,decy,nrj,tech,victory,current,maxnrj,maxrayon,maxcycle,maxtemp,nom,descriptif,element
	loc=[0,0,1,1]
	''' Directions des electrons en fonction de la position de la queue '''
	direction = {}
	direction[(-1,-1)]=[(+1,+1),(+1,+0),(+0,+1),(+1,-1),(-1,+1),(+0,-1),(-1,+0),(-1,-1)]
	direction[(-1,+0)]=[(+1,+0),(+1,-1),(+1,+1),(+0,-1),(+0,+1),(-1,-1),(-1,+1),(-1,+0)]
	direction[(-1,+1)]=[(+1,-1),(+0,-1),(+1,+0),(-1,-1),(+1,+1),(-1,+0),(+0,+1),(-1,+1)]
	direction[(+0,+1)]=[(+0,-1),(-1,-1),(+1,-1),(-1,+0),(+1,+0),(-1,+1),(+1,+1),(+0,+1)]
	direction[(+0,-1)]=[(+0,+1),(+1,+1),(-1,+1),(+1,+0),(-1,+0),(+1,-1),(-1,-1),(+0,-1)]
	direction[(+1,-1)]=[(-1,+1),(+0,+1),(-1,+0),(+1,+1),(-1,-1),(+1,+0),(+0,-1),(+1,-1)]
	direction[(+1,+0)]=[(-1,+0),(-1,+1),(-1,-1),(+0,+1),(+0,-1),(+1,+1),(+1,-1),(+1,+0)]
	direction[(+1,+1)]=[(-1,-1),(-1,+0),(+0,-1),(-1,+1),(+1,-1),(+0,+1),(+1,+0),(+1,+1)]
	adirection=[(-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)]
	savenames=["α","β","γ","δ","ε","ζ","η","θ","ι","κ","λ","μ","ν","ξ","ο","π","ρ","ς","σ","τ","υ","φ","χ","ψ","ω"]
	verifyhome()
	read("dbdata")
	read(gethome()+"/dbdata")
	reference(worlds,['world','level'])
	reference(Uworlds,['world','level'])
	duplicateref(art)
	loadpic(menus)
	''' Variables globales '''
	zoom=25
	stat=[0,0,0,0,0,0,0,0,0]
	nom=descriptif=element='H'
	victory=[0,0,0,0,0,0,0,0,0,0,0,0,0]
	current=[0,0,0,0,0,0,0,0,0,0,0,0,0]
	users=[]
	stat_var=[]
	maxnrj=maxrayon=maxcycle=maxtemp=99999
	allcout=[0,0,0]
	sizex=sizey=1
	seestat=thecout=world=over=play=cycle=rayon=temp=cout=decx=decy=nrj=0
	rect=0
	debug=False
	msg=tuto=''
	tech=selected=level=-1
	statedvar=[stat[0],stat[1],stat[2],stat[3],stat[4],stat[5],stat[6],stat[7],stat[8],nrj,temp,rayon,current[7],current[8],current[9],current[10],current[11],current[12]]
	if len(stat_var)==0:
		for i in range(len(statedvar)):
			stat_var.append([0])
	world_new = world_art = [[]]
	world=0
	for w in range(len(worlds)):
		for l in range(len(worlds[w])):
			if "level"+str(w)+"-"+str(l) in finished and w>world:
				world=w
				
	if len(sys.argv)>1 and sys.argv[1]=='debug': debug=True


''' *********************************************************************************************** '''
''' Sauvegarde/Restauration																								 '''
					
def resize():
	global zoom,decx,decy,seestat
	if seestat>=1:
		allsizex=2*win.width/3
	else:
		allsizex=win.width
	if (sizex-2)/float(sizey-2)<allsizex/(win.height-102.0):
		zoom=(win.height-102-4)/(sizey-2)
	else:
		zoom=(allsizex-4)/(sizex-2)
	decx=-zoom+(allsizex-zoom*(sizex-2))/2
	decy=-zoom+(win.height-zoom*(sizey-2))/2

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
''' Fonctions programmees																							 '''

def prog_menu(dt,leveler):
	global level,over
	level=leveler
	over=0
		
def prog_calculate(dt):
	nextgrid()
	
def prog_refresh(dt):
	global world,level
	if player.source and player.source.video_format:
		glColor3ub(255,255,255)
		player.get_texture().blit(0,0,width=win.width,height=win.height)
		return
	win.clear()
	if level==-2:	
		drawsettings()
	elif level!=-1:
		drawgrid(zoom)
	else:
		drawworld()
	
''' *********************************************************************************************** '''
''' Affichage																						'''	

def drawcumulgraph(coords,tableau,full,color):
	drawsquare(coords[0],coords[1],coords[2],coords[3],1,[100,100,100])
	tab=copy.deepcopy(tableau)
	newtab=[tab[0]]
	for i in range(1,len(tab)):
		newtab.append(tab[i])
		for j in range(len(tab[i])):	
			newtab[i][j]=newtab[i][j]+newtab[i-1][j]
	sizey=max(tab[len(tab)-1])
	if sizey==0:
		sizey=coords[3]-coords[1]	
	else:
		sizey=(coords[3]-coords[1])/float(sizey)
	if len(tab[0])-1>0:
		sizex=(coords[2]-coords[0])/float(len(tab[0]))
	else:
		sizex=coords[2]-coords[0]
	glColor3ub(140,140,140)
	scalex=10*int((60/sizex)/10)
	scaley=10*int((80/sizey)/10)
	if scalex==0: scalex=1
	if scaley==0: scaley=1	
	for n in range(0,len(newtab[0]),scalex):
			glBegin(GL_LINES)
			glVertex2i(coords[0]+int(sizex*n),coords[1])
			glVertex2i(coords[0]+int(sizex*n),coords[3])
			glEnd()
	for n in range(0,max(tab[len(tab)-1]),scaley):
			glBegin(GL_LINES)
			glVertex2i(coords[0],coords[1]+int(sizey*n))
			glVertex2i(coords[2],coords[1]+int(sizey*n))
			glEnd()
	for i in range(len(newtab)):
		glBegin(GL_QUADS)
		for j in range(len(newtab[i])):
			glColor4ub(color[i][0],color[i][1],color[i][2],220) 	
			glVertex2i(int(coords[0]+sizex*j),int(coords[1]+sizey*newtab[i][j]))	
			glVertex2i(int(coords[0]+sizex*(j+1)),int(coords[1]+sizey*newtab[i][j]))
			if i>0:
				glVertex2i(int(coords[0]+sizex*(j+1)),int(coords[1]+sizey*newtab[i-1][j]))
				glVertex2i(int(coords[0]+sizex*j),int(coords[1]+sizey*newtab[i-1][j]))
			else:			
				glVertex2i(int(coords[0]+sizex*(j+1)),int(coords[1]))
				glVertex2i(int(coords[0]+sizex*j),int(coords[1]))
		glEnd()
	glBegin(GL_QUADS)
	glColor3ub(255,255,255)
	glVertex2i(int(coords[2]),int(coords[1]))
	glVertex2i(int(coords[2]-5),int(coords[1]))
	glVertex2i(int(coords[2]-5),int(coords[1]+sizey))
	glVertex2i(int(coords[2]),int(coords[1]+sizey))
	glVertex2i(int(coords[2]),int(coords[1]))
	glVertex2i(int(coords[2]-sizex),int(coords[1]))
	glVertex2i(int(coords[2]-sizex),int(coords[1]+5))
	glVertex2i(int(coords[2]),int(coords[1]+5))
	glEnd()	
			
def drawgraph(coords,tab,full,color):
	drawsquare(coords[0],coords[1],coords[2],coords[3],1,[100,100,100])
	if max(tab)==0:
		sizey=coords[3]-coords[1]
	else:
		sizey=(coords[3]-coords[1])/float(max(tab))
	if len(tab)-1>0:
		sizex=(coords[2]-coords[0])/float(len(tab))
	else:
		sizex=coords[2]-coords[0]
	glColor3ub(140,140,140)
	scalex=10*int((60/sizex)/10)
	scaley=10*int((80/sizey)/10)
	if scalex==0: scalex=1
	if scaley==0: scaley=1	
	for n in range(0,len(tab),scalex):
			glBegin(GL_LINES)
			glVertex2i(coords[0]+int(sizex*n),coords[1])
			glVertex2i(coords[0]+int(sizex*n),coords[3])
			glEnd()
	for n in range(0,int(max(tab))+1,scaley):
			glBegin(GL_LINES)
			glVertex2i(coords[0],coords[1]+int(sizey*n))
			glVertex2i(coords[2],coords[1]+int(sizey*n))
			glEnd()
	glColor4ub(color[0],color[1],color[2],220) 
	if full>0:
		glBegin(GL_QUADS)
		for i in range(len(tab)):
			glVertex2i(int(coords[0]+sizex*i),int(coords[1]+sizey*tab[i]))
			glVertex2i(int(coords[0]+sizex*(i+1)),int(coords[1]+sizey*tab[i]))
			glVertex2i(int(coords[0]+sizex*(i+1)),int(coords[1]))
			glVertex2i(int(coords[0]+sizex*i),int(coords[1]))
		glEnd()
	else:
		glBegin(GL_LINE_LOOP)
		for i in range(len(tab)):
			glVertex2i(int(coords[0]+sizex*i),int(coords[1]+sizey*tab[i]))
		glEnd()
	glBegin(GL_QUADS)
	glColor3ub(255,255,255)
	glVertex2i(int(coords[2]),int(coords[1]))
	glVertex2i(int(coords[2]-5),int(coords[1]))
	glVertex2i(int(coords[2]-5),int(coords[1]+sizey))
	glVertex2i(int(coords[2]),int(coords[1]+sizey))
	glVertex2i(int(coords[2]),int(coords[1]))
	glVertex2i(int(coords[2]-sizex),int(coords[1]))
	glVertex2i(int(coords[2]-sizex),int(coords[1]+5))
	glVertex2i(int(coords[2]),int(coords[1]+5))
	glEnd()											
    
def drawsquare(x,y,x2,y2,full,color):
	if len(color)==4:
		glColor4ub(color[0],color[1],color[2],color[3]) 	
	else:
		glColor3ub(color[0],color[1],color[2]) 
	if full>0:
		glBegin(GL_QUADS)
	else:
		glBegin(GL_LINE_LOOP)
	glVertex2i(x,y)
	glVertex2i(x2,y)
	glVertex2i(x2,y2)
	glVertex2i(x,y2)
	glEnd()
	if full==2:
		glColor3ub(color[0],color[1],color[2])
		glBegin(GL_LINE_LOOP)
		glVertex2i(x,y)
		glVertex2i(x2,y)
		glVertex2i(x2,y2)
		glVertex2i(x,y2)
		glEnd()
		
def drawarrow(x,y,x2,y2,color):
	glColor3ub(color[0],color[1],color[2]) 
	glBegin(GL_LINE_LOOP)
	glVertex2i(x,y)
	glVertex2i(x2,y2)
	glEnd()
	angle=math.atan(float(y2-y)/(x2-x))
	if y2<y and x2<x: angle=angle+180*3.14/180
	glBegin(GL_POLYGON)
	glVertex2i(x2,y2)
	glVertex2i(int(20*math.cos(angle+160*3.14/180))+x2,int(20*math.sin(angle+160*3.14/180))+y2)
	glVertex2i(int(10*math.cos(angle+180*3.14/180))+x2,int(10*math.sin(angle+180*3.14/180))+y2)	
	glVertex2i(int(20*math.cos(angle-160*3.14/180))+x2,int(20*math.sin(angle-160*3.14/180))+y2)	
	glEnd()	
	
def drawsemisquare(x,y,x2,y2,color):
	if len(color)==4:
		glColor4ub(color[0],color[1],color[2],color[3]) 	
	else:
		glColor3ub(color[0],color[1],color[2]) 
	glBegin(GL_LINES)
	thezoom=y2-y
	glVertex2i(x,y)
	glVertex2i(x,y+thezoom/4)
	glVertex2i(x,y)
	glVertex2i(x+thezoom/4,y)
	glVertex2i(x2,y2)
	glVertex2i(x2,y2-thezoom/4)
	glVertex2i(x2,y2)
	glVertex2i(x2-thezoom/4,y2)
	glVertex2i(x,y2)
	glVertex2i(x,y2-thezoom/4)
	glVertex2i(x,y2)
	glVertex2i(x+thezoom/4,y2)
	glVertex2i(x2,y)
	glVertex2i(x2,y+thezoom/4)
	glVertex2i(x2,y)
	glVertex2i(x2-thezoom/4,y)
	glEnd()
	
def drawtriangles(x,y,x2,y2,color):
	if len(color)==4:
		glColor4ub(color[0],color[1],color[2],color[3]) 	
	else:
		glColor3ub(color[0],color[1],color[2]) 
	glBegin(GL_TRIANGLES)
	thezoom=y2-y
	glVertex2i(x,y)
	glVertex2i(x,y+thezoom/4)
	glVertex2i(x+thezoom/4,y)
	glVertex2i(x2,y2)
	glVertex2i(x2,y2-thezoom/4)
	glVertex2i(x2-thezoom/4,y2)
	glVertex2i(x,y2)
	glVertex2i(x,y2-thezoom/4)
	glVertex2i(x+thezoom/4,y2)
	glVertex2i(x2,y)
	glVertex2i(x2,y+thezoom/4)
	glVertex2i(x2-thezoom/4,y)
	glEnd()

def drawLaser(x1,y1,x2,y2,width,power,color,randomize):
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
	
def drawitem(x,y,it,thezoom,activation):
	if 'text' in it:
		txt_item.text=it['text'].decode('utf-8')
		txt_item.font_size=thezoom
		txt_item.x=x+thezoom/10
		txt_item.y=y+thezoom/10
		if not it['activable']:
			txt_item.color=(it['color'][0],it['color'][1],it['color'][2],255)
		else:
			if activation!=0:
				drawtriangles(x+1,y+1,x+thezoom-1,y+thezoom-1,[it['color'][0],it['color'][1],it['color'][2],55+200*activation/10])
				txt_item.color=(it['color'][0],it['color'][1],it['color'][2],55+200*activation/10)
			else:
				drawtriangles(x+1,y+1,x+thezoom-1,y+thezoom-1,[255,255,255])
				txt_item.color=(255,255,255,255)
		txt_item.draw()
		
def drawstat(x,y,x2,y2,tableau,color):
	global stat
	drawsquare(x+1,y+1,x2,y2,0,[90,90,90])
	oldx=x
	somme=sum(tableau)
	for i in range(len(tableau)):
		if somme>0:
			newx=oldx+float(tableau[i])*(x2-x)/somme
		else:
			newx=oldx
		drawsquare(int(oldx),y,int(newx),y2,1,color[i])
		oldx=newx
	txt_stat.text=str(somme)
	txt_stat.x=x+(x2-x)/2-(len(str(somme)))*12
	txt_stat.y=y-(y-24)/2
	txt_stat.draw()
	
def drawcondvictory(x,y,x2,y2,color):
	global victory,current
	'''size=(x2-x)/sum(victory[i] for i in range(len(victory)))'''
	names=["e","e","q","e","e","e","e","K","L","M","N","n","p"]
	thecolors=[art['headb2']['color'],art['headb']['color'],art['headp']['color'],art['head']['color'],art['head2']['color'],art['headr']['color'],art['headr2']['color'],art['headb']['color'],art['headb']['color'],art['headb']['color'],art['headb']['color'],art['neut']['color'],art['prot']['color']]
	size=21
	for i in range(len(victory)):
		if victory[i]>0: 
			drawsquare(x+size*i,y,x+size*(i+1),y2,1,thecolors[i])
			drawsquare(x+size*i,y,x+size*(i+1),y2,0,[90,90,90])
			drawsquare(x+size*i,y,x+size*(i+1),int(y+float(current[i])/victory[i]*(y2-y)),1,[0,0,0])
			if victory[i]-current[i]>=0:
				txt_victory1.text=str(victory[i]-current[i])
				txt_victory1.x=x+size*i+1
				txt_victory1.y=y+1
				txt_victory1.draw()
			txt_victory2.text=names[i]
			txt_victory2.x=x+size*i
			txt_victory2.y=y2-10
			txt_victory2.draw()
			
def drawsettings():
	pic_logo.blit((win.width-668)/2,win.height-200)
	pic_logo2.blit((win.width-668)/2-120,win.height-160)
	txt_son.x=win.width/6
	txt_son.y=win.height/6
	txt_son.draw()
	txt_video.x=win.width/6
	txt_video.y=2*win.height/6	
	txt_video.draw()
			
def drawworld():
	global selected,victory,finished,world,level,loc
	loc[0]+=loc[2]
	loc[1]+=loc[3]
	if loc[0]>1024:
		loc[2]=-1
	if loc[1]>768:
		loc[3]=-1
	if loc[0]<0:
		loc[2]=1
	if loc[1]<0:
		loc[3]=1
	glColor4ub(255,255,255,200)
	pic_test.blit(loc[0],loc[1])
	pic_test.blit(loc[0]-1024,loc[1])
	pic_test.blit(loc[0]-1024,loc[1]-768)
	pic_test.blit(loc[0],loc[1]-768)
	glColor3ub(255,255,255)
	for obj in worlds[world]:
		if obj.has_key('special'):
			break	
	txt_obj.text=obj['element']
	txt_obj.color=(color_leveler[world][0],color_leveler[world][1],color_leveler[world][2],100)
	txt_obj.x=(1024-txt_obj.content_width)/2-50
	txt_obj.y=75*win.height/768
	txt_obj.draw()
	drawsquare(740,148,1016,8,1,[40,40,40])
	drawsquare(8,148,1016,8,0,[90,90,90])
	glColor3ub(255,255,255)	
	pic_logo.blit(185,win.height-200)
	pic_logo2.blit(45,win.height-150)
	if selected==-2:
		glColor3ub(255,0,0)
	else:
		glColor3ub(255,255,255)

	pic_exit2.blit(940,win.height-100)
	if selected==-3:
		glColor3ub(255,0,0)
	else:
		glColor3ub(255,255,255)
	pic_arrows.blit(840,150)
	if selected==-4:
		glColor3ub(255,0,0)
	else:
		glColor3ub(255,255,255)
	pic_arrows2.blit(920,150)
	glColor3ub(255,255,255)	
	for l in range(len(worlds[world])):
		ele=worlds[world][l]
		for n in ele['link']:
			if n!="" and n[0]==world:
				if n in finished:
					drawLaser(ele['_xx']+50,int(ele['_yy']/768.0*win.height+50),worlds[n[0]][n[1]]['_xx']+50,int(worlds[n[0]][n[1]]['_yy']/768.0*win.height+50),random.randint(0,8),20,color_leveler[world],12)	
				else:
					drawLaser(ele['_xx']+50,int(ele['_yy']/768.0*win.height+50),worlds[n[0]][n[1]]['_xx']+50,int(worlds[n[0]][n[1]]['_yy']/768.0*win.height+50),2,20,[40,40,40],0)		
	for l in range(len(worlds[world])):
		ele=worlds[world][l]
		if (world,l) not in finished:
			glColor3ub(60,60,60)
			acolor=(90,90,90,255)
		elif selected!=ele:
			glColor3ub(255,120+int(ele['_xx']/1024.0*135),155+int(ele['_xx']/1024.0*100))
			acolor=(255,255,255,255)
		else:
			acolor=(255,0,0,255)
			document=pyglet.text.decode_attributed("{font_name 'OpenDyslexicAlta'}{font_size 18}{color (255, 255, 255, 255)}"+ele['description'].decode('utf-8')+"}".encode('utf8'))
			txt_description.document=document
			txt_description.draw()
			document=None
			glColor3ub(255,255,255)
			if ele['cout']>0:
				pic_cout.blit(740,110)
				txt_cout2.text=str(ele['cout'])
				txt_cout2.draw()
			if ele['maxcycle']<90000:
				pic_cycle.blit(740,65)
				txt_maxcycle2.text=str(ele['maxcycle'])
				txt_maxcycle2.draw()
			if ele['tech']>0:	
				pic_tech.blit(940,110)
				txt_tech2.text=str(ele['tech'])
				txt_tech2.draw()
			if ele['maxrayon']<90000:	
				pic_rayon.blit(940,65)
				txt_maxrayon2.text=str(ele['maxrayon'])
				txt_maxrayon2.draw()
			if ele['maxtemp']<90000:	
				pic_temp.blit(850,110)
				txt_maxtemp2.text=str(ele['maxtemp'])
				txt_maxtemp2.draw()
			if ele['maxnrj']<90000:	
				pic_nrj.blit(850,65)
				txt_maxnrj2.text=str(ele['maxnrj'])
				txt_maxnrj2.draw()
			victory=ele['victory']
			drawcondvictory(742,12,1016,50,[40,40,40])
			glColor3ub(255,0,0)
		pic_leveler[world].blit(ele['_xx'],ele['_yy']/768.0*win.height)
		glColor3ub(255,255,255)
		txt_element2.text=ele['element']
		txt_element2.x=ele['_xx']+(pic_leveler[world].width-txt_element2.content_width)/2
		txt_element2.y=ele['_yy']/768.0*win.height+20
		txt_element2.color=(int(ele['_xx']/1024.0*150), int(ele['_xx']/1024.0*150), int(ele['_xx']/1024.0*150),255)
		txt_element2.draw()
		if (world,l) not in finished:
			glColor3ub(255,255,255)
			pic_locked.blit(ele['_xx']+10,ele['_yy']/768.0*win.height+50)
		txt_nom2.text=ele['nom'].decode('utf-8')
		calc=(txt_nom2.content_width-pic_leveler[world].width)/2
		'''drawsquare(ele['_xx']-calc,int(ele['_yy']/768.0*win.height+2),ele['_xx']-calc+txt_nom2.content_width,int(ele['_yy']/768.0*win.height-18),1,[40,int(ele['_xx']/1024.0*135),int(ele['_xx']/1024.0*100)])		'''	
		txt_nom2.x=ele['_xx']-calc
		txt_nom2.y=ele['_yy']/768.0*win.height-15
		txt_nom2.color=acolor
		txt_nom2.draw()
		if ele.has_key('special'):
			glColor3ub(255,255,255)
			pic_special.blit(ele['_xx']+70,ele['_yy']/768.0*win.height)
			
def calc_space(nb,nbtot):
	return [2*win.width/3+20,(nb-1)*(win.height-100)/nbtot+50+20,win.width-20,nb*(win.height-100)/nbtot+50]

def drawpopup():
	global allcout
	if type(allcout[2]) is str:
		txt_drag.x=allcout[0]-txt_drag.content_width/2
		if txt_drag.x<0:
			txt_drag.x=0
		if txt_drag.x+txt_drag.content_width>win.width:
			txt_drag.x=win.width-txt_drag.content_width
		txt_drag.y=allcout[1]+6
		txt_drag.text=allcout[2]
		drawsquare(txt_drag.x-3,allcout[1],txt_drag.x+txt_drag.content_width+3,allcout[1]+25,1,[40,40,40])
		drawsquare(txt_drag.x-3,allcout[1],txt_drag.x+txt_drag.content_width+3,allcout[1]+25,0,[255,255,255])
		txt_drag.draw()
		return
	if tech<6:
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+75,1,[40,40,40])
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+75,0,[255,255,255])
	else:
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+150,1,[40,40,40])
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+150,0,[255,255,255])
	txt_drag.x=allcout[0]+45
	txt_drag.y=allcout[1]+10
	glColor3ub(255,255,255,255)
	pic_cout.blit(allcout[0]+2,allcout[1]+2)
	txt_drag.text=str(allcout[2]['cout'])
	txt_drag.draw()
	txt_drag.x=allcout[0]+45
	txt_drag.y=allcout[1]+45
	glColor3ub(255,255,255,255)
	pic_tech.blit(allcout[0]+2,allcout[1]+37)
	txt_drag.text=str(allcout[2]['tech'])
	txt_drag.draw()
	if tech>6:
		txt_drag.x=allcout[0]+45
		txt_drag.y=allcout[1]+80
		glColor3ub(255,255,255,255)
		pic_nrj.blit(allcout[0]+2,allcout[1]+72)
		txt_drag.text=str(allcout[2]['nrj'])
		txt_drag.draw()	
		txt_drag.x=allcout[0]+45
		txt_drag.y=allcout[1]+115
		glColor3ub(255,255,255,255)
		pic_temp.blit(allcout[0]+2,allcout[1]+107)
		txt_drag.text=str(allcout[2]['temp'])
		txt_drag.draw()	

def drawbigstat(page):	
	global stat_var	
	drawsquare(2*win.width/3,50,win.width,win.height-50,1,[40,40,40])
	if page==1:
		coord=calc_space(1,3)
		drawcumulgraph(calc_space(1,3),[stat_var[0],stat_var[1],stat_var[3],stat_var[4],stat_var[5],stat_var[6]],1,[art['headb2']['color'],art['headb']['color'],art['head']['color'],art['head2']['color'],art['headr']['color'],art['headr2']['color']])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="eX"
		txt_victory2.draw()	
		coord=calc_space(2,3)			
		drawcumulgraph(calc_space(2,3),[stat_var[7],stat_var[8]],1,[art['neut']['color'],art['prot']['color']])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+8
		txt_victory2.y=coord[1]+12
		txt_victory2.text="p/n"
		txt_victory2.draw()	
		coord=calc_space(3,3)
		drawgraph(calc_space(3,3),stat_var[2],1,art['headp']['color'])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="Ph"
		txt_victory2.draw()	
	elif page==2:
		coord=calc_space(1,3)
		drawgraph(coord,stat_var[9],1,[180,180,180])
		pic_nrj.blit(coord[0],coord[1])
		coord=calc_space(2,3)
		drawgraph(coord,stat_var[10],1,[180,180,180])
		pic_temp.blit(coord[0],coord[1])
		coord=calc_space(3,3)
		drawgraph(coord,stat_var[11],1,[180,180,180])
		pic_rayon.blit(coord[0],coord[1])
	elif page==3:
		coord=calc_space(1,6)
		drawgraph(coord,stat_var[17],1,art['prot']['color'])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="p"
		txt_victory2.draw()
		coord=calc_space(2,6)
		drawgraph(coord,stat_var[16],1,art['neut']['color'])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="n"
		txt_victory2.draw()
		coord=calc_space(3,6)
		drawgraph(coord,stat_var[15],1,art['headb']['color'])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="N"
		txt_victory2.draw()
		coord=calc_space(4,6)
		drawgraph(coord,stat_var[14],1,art['headb']['color'])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="M"
		txt_victory2.draw()
		coord=calc_space(5,6)
		drawgraph(coord,stat_var[13],1,art['headb']['color'])
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="L"
		txt_victory2.draw()
		coord=calc_space(6,6)
		drawgraph(coord,stat_var[12],1,art['headb']['color'])	
		drawsquare(coord[0],coord[1],coord[0]+36,coord[1]+36,1,[40,40,40])
		txt_victory2.x=coord[0]+12
		txt_victory2.y=coord[1]+12
		txt_victory2.text="K"
		txt_victory2.draw()
		
def drawgameover():
	txt_over.text="GAME OVER"
	txt_over.x=win.width/2-350
	txt_over.y=win.height/2-200
	txt_over.draw()
	msg=["Trop de matière reçue dans les senseurs","Les photons sont sortis du cadre de jeu","Colision de protons et de neutrons","Le canon a provoqué une collision","Vous avez généré trop de rayonements","Le nombre de cycle maximum a été atteint","La température est a un niveau inacceptable","Il n'y a plus d'energie disponible !","Le réacteur est en surcharge !!"]
	txt_over2.text=msg[over-1].decode('utf-8')
	txt_over2.x=win.width/2-450
	txt_over2.y=win.height/2-90
	txt_over2.draw()
		
def drawvictory():
	txt_over.text="VICTOIRE !"
	txt_over.x=win.width/2-350
	txt_over.y=win.height/2-200
	txt_over.draw()
	txt_over2.text="Vous débloquez le/les niveaux suivant.".decode('utf-8')
	txt_over2.x=win.width/2-450
	txt_over2.y=win.height/2-90
	txt_over2.draw()
	
def drawelement(x,y,x2,y2):
	global element,world,level,worlds
	drawsquare(x,y,x2,y2,1,[240,int(worlds[world][level]['_xx']/1024.0*120+100), int(worlds[world][level]['_xx']/1024.0*120+100)])
	txt_element.text=element
	txt_element.color=(int(worlds[world][level]['_xx']/1024.0*150),int(worlds[world][level]['_xx']/1024.0*150), int(worlds[world][level]['_xx']/1024.0*150),255)
	txt_element.x=x+(x2-x-txt_element.content_width)/2
	txt_element.y=y+5
	txt_element.draw()
	
def drawmenu(themenus):
	global tech,play
	for i in range(len(themenus)):
		if themenus[i][0]['visible']:
			if themenus[i][0]['place']=='bottom':
				drawsquare(0,themenus[i][0]['size'],win.width,0,1,[40,40,40])
				placey=0
			elif themenus[i][0]['place']=='top':
				drawsquare(0,win.height,win.width,win.height-themenus[i][0]['size'],1,[40,40,40])
				placey=win.height-themenus[i][0]['size']
			else:
				for search in themenus:
					if search[0]['place']=='bottom':
						drawsquare(0,search[0]['size'],win.width,search[0]['size']+themenus[i][0]['size'],1,[40,40,40])
						placey=search[0]['size']
						break
			sizeofall=0
			variables=0
			if themenus[i][0]['variable']:
				themenus[i][0]['size']=win.width/len(themenus[i])-1
				for j in range(1,len(themenus[i])):
					themenus[i][j]['size']=themenus[i][0]['size']
					if (type(themenus[i][j]['icon']) is dict):
						themenus[i][j]['icon']['size']=themenus[i][0]['size']-12
			for j in range(1,len(themenus[i])):
				if type(themenus[i][j]['visible']) is str and eval(themenus[i][j]['visible']) or (type(themenus[i][j]['visible']) is not str and themenus[i][j]['visible']):
					if not themenus[i][j]['variable']:
						sizeofall+=themenus[i][j]['size']
					else:
						variables+=1
			for j in range(1,len(themenus[i])):
				if themenus[i][j]['variable'] and (type(themenus[i][j]['visible']) is str and eval(themenus[i][j]['visible']) or (type(themenus[i][j]['visible']) is not str and themenus[i][j]['visible'])):
					themenus[i][j]['size']=(win.width-sizeofall)/variables
			placex=10
			for j in range(1,len(themenus[i])):
				placetemp=placex
				if themenus[i][j]['size']<30: continue
				if type(themenus[i][j]['visible']) is str and not eval(themenus[i][j]['visible']) or not themenus[i][j]['visible']: continue
				if themenus[i][j]['tech']>tech: 
					placex+=themenus[i][j]['size']
					continue
				if type(themenus[i][j]['icon']) is list:
					if type(themenus[i][j]['icon'][0]) is not int:
						if (type(themenus[i][j]['active']) is str and eval(themenus[i][j]['active'])) or (type(themenus[i][j]['active']) is not str and themenus[i][j]['active']) :
							glColor3ub(255,255,255)
						else:
							glColor4ub(255,255,255,40)
						themenus[i][j]['icon'][themenus[i][j]['choose']].blit(placex,placey+(themenus[i][0]['size']-themenus[i][j]['icon'][themenus[i][j]['choose']].height)/2)
						placetemp+=themenus[i][j]['icon'][themenus[i][j]['choose']].width
					else:
						drawsquare(placex,placey+(themenus[i][0]['size']-36)/2,placex+36,placey+(themenus[i][0]['size']-36)/2+37,1,themenus[i][j]['icon'])
				elif type(themenus[i][j]['icon']) is dict:
					if themenus[i][j]['icon'].has_key('color') and themenus[i][j]['icon'].has_key('colorise'):
						if ((type(themenus[i][j]['active']) is str and eval(themenus[i][j]['active'])) or (type(themenus[i][j]['active']) is not str and themenus[i][j]['active'])):
							themenus[i][j]['icon']['color']=(220,220,220)
						else:
							themenus[i][j]['icon']['color']=(40,40,40)
					if themenus[i][j]['icon'].has_key('size'):
						drawitem(placex,placey+(themenus[i][0]['size']-themenus[i][j]['icon']['size'])/2,themenus[i][j]['icon'],themenus[i][j]['icon']['size'],10)
					else:
						drawitem(placex,placey+(themenus[i][0]['size']-themenus[i][j]['size'])/2,themenus[i][j]['icon'],themenus[i][j]['size'],10)
				elif type(themenus[i][j]['icon']) is str:
					if themenus[i][j].has_key('params'):
						eval(themenus[i][j]['icon']+"("+str(placex)+","+str(placey+(themenus[i][0]['size']-36)/2)+","+str(placex+themenus[i][j]['size'])+","+str(placey+(themenus[i][0]['size']-36)/2+37)+","+themenus[i][j]['params']+")")
					else:
						eval(themenus[i][j]['icon']+"("+str(placex)+","+str(placey+(themenus[i][0]['size']-36)/2)+","+str(placex+themenus[i][j]['size'])+","+str(placey+(themenus[i][0]['size']-36)/2+37)+")")
				else:
					if (type(themenus[i][j]['active']) is str and eval(themenus[i][j]['active'])) or (type(themenus[i][j]['active']) is not str and themenus[i][j]['active']):
						glColor3ub(255,255,255)
					else:
						glColor4ub(255,255,255,60)
					themenus[i][j]['icon'].blit(placex,placey+(themenus[i][0]['size']-themenus[i][j]['icon'].height)/2)
					placetemp+=themenus[i][j]['icon'].width
				if themenus[i][j]['squarred']:
					if int(time.time())%2==0: drawsquare(placex,placey+(themenus[i][0]['size']-36)/2,placex+36,placey+(themenus[i][0]['size']-36)/2+37,1,[255,0,0,110])
				if themenus[i][j]['separe']:
					drawsquare(placex+themenus[i][j]['size']-5,placey+5,placex+themenus[i][j]['size']-3,placey+themenus[i][0]['size']-5,1,[90,90,90])
				if themenus[i][j].has_key('text2'):
					txt_cout.text=themenus[i][j]['text']
					if txt_cout.text[0]=="#":
						txt_cout.text=eval(txt_cout.text[1:])
					if int(txt_cout.text)<0:
						txt_cout.color=(255, 0, 0,255)
					elif not themenus[i][j]['active']:
						txt_cout.color=(40,40,40,255)
					else:
						txt_cout.color=(180, 180, 180,255)
					txt_cout.x=placetemp
					txt_cout.y=placey+1
					txt_cout.draw()		
				elif themenus[i][j].has_key('text'):
					txt_cout.text=themenus[i][j]['text']
					if txt_cout.text[0]=="#":
						txt_cout.text=eval(txt_cout.text[1:])
					if int(txt_cout.text)<0:
						txt_cout.color=(255, 0, 0,255)
					elif not themenus[i][j]['active']:
						txt_cout.color=(40,40,40,255)
					else:
						txt_cout.color=(180, 180, 180,255)
					txt_cout.x=placetemp
					txt_cout.y=placey+15
					txt_cout.draw()
				if themenus[i][0]['selectable']:
					if (themenus[i][0]['mouse'][0]==j):
						selectcolor=[255,0,0,40] 
					elif (themenus[i][0]['mouse'][1]==j):
						selectcolor=[0,255,0,40]  
					elif (themenus[i][0]['mouse'][2]==j):
						selectcolor=[0,0,255,40] 
					if ((themenus[i][0]['mouse'][0]==j) or (themenus[i][0]['mouse'][1]==j) or (themenus[i][0]['mouse'][2]==j)):
						if play>0:
							glLineWidth(random.randint(1,3))
							glLineStipple(random.randint(0,10),random.randint(0,65535))	
						drawsquare(placex,placey+(themenus[i][0]['size']-36)/2,placex+37,placey+(themenus[i][0]['size']-36)/2+37,2,selectcolor)
					if ((themenus[i][0]['mouse'][0]==j) or (themenus[i][0]['mouse'][1]==j) or (themenus[i][0]['mouse'][2]==j)):
						if play>0:
							glLineStipple(random.randint(0,10),random.randint(0,65535))
						drawsquare(placex-1,placey+(themenus[i][0]['size']-36)/2-1,placex+38,placey+(themenus[i][0]['size']-36)/2+38,2,selectcolor)
					glLineStipple(0,65535)
					glLineWidth(1)
				placex+=themenus[i][j]['size']
	return
	
def drawtuto():
	global tuto,rect,msg,menus
	drawsquare(win.width-384,menus[0][0]['size'],win.width,menus[0][0]['size']+200,2,[40,40,40,200])	
	if type(rect) is list:
		if rect[4]==0:
			drawsquare(rect[0]*win.width/1024,rect[1]*win.height/768,rect[2]*win.width/1024,rect[3]*win.height/768,2,[255,0,0,20])
		else:
			drawarrow(rect[0]*win.width/1024,rect[1]*win.height/768,rect[2]*win.width/1024,rect[3]*win.height/768,[255,0,0])
	txt_message.x=win.width-384
	txt_message.y=menus[0][0]['size']
	document=pyglet.text.decode_attributed("{font_name 'OpenDyslexicAlta'}{font_size 18}{color (255, 255, 255, 255)}"+msg.decode('utf-8')+"}".encode('utf8'))
	txt_message.document=document
	txt_message.draw()
			
def drawgrid(zoom):
	global temp,debug,over,allcout,play,element,seestat,art,users,menus,tuto
	glLineWidth(3)
	if play>0:
		drawsquare(decx-1+zoom,decy-1+zoom,decx+zoom*(sizex-1)+1,decy+zoom*(sizey-1)+2,0,[255,0,0])	
	else:
		drawsquare(decx-1+zoom,decy-1+zoom,decx+zoom*(sizex-1)+1,decy+zoom*(sizey-1)+2,0,[255,255,255])
	glLineWidth(1)	
	for x in range(1,sizex-1):
		if x*zoom+decx>win.width: break
		for y in range(1,sizey-1):
			if y*zoom+decy>win.height: break
			'''drawsquare(x*zoom+decx,y*zoom+decy,(x+1)*zoom+decx,(y+1)*zoom+decy,1,art[world_new[x][y]]['color'])'''
			glBegin(GL_QUADS)
			if world_new[x-1][y-1]>0 or (world_new[x-1][y]>0 and world_new[x][y-1]>0):
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],255)
			else:
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],130)
			glVertex2i(x*zoom+decx,y*zoom+decy)
			if world_new[x+1][y-1]>0 or (world_new[x+1][y]>0 and world_new[x][y-1]>0):
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],255)
			else:
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],130)
			glVertex2i((x+1)*zoom+decx,y*zoom+decy)
			if world_new[x+1][y+1]>0 or (world_new[x][y+1]>0 and world_new[x+1][y]>0):
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],255)
			else:
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],130)
			glVertex2i((x+1)*zoom+decx,(y+1)*zoom+decy)
			if world_new[x-1][y+1]>0 or (world_new[x][y+1]>0 and world_new[x-1][y]>0):
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],255)
			else:
				glColor4ub(art[world_new[x][y]]['color'][0],art[world_new[x][y]]['color'][1],art[world_new[x][y]]['color'][2],130)
			glVertex2i(x*zoom+decx,(y+1)*zoom+decy)
			glEnd()
			drawitem(x*zoom+decx,y*zoom+decy,art[wart(x,y)],zoom,getactive(x,y))
	drawmenu(menus)
	if seestat>=1: drawbigstat(seestat)
	if over>0: drawgameover()
	if over<0: drawvictory()
	if tuto!='' and menus[0][12]['choose']==1: drawtuto()
	if allcout[2]>0: drawpopup()
	return	
		

''' *********************************************************************************************** '''
''' Fonctions gestion du monde																		'''

def reallystop():
	global play,world,level,stat,stat_var,current,cycle,temp,nrj,rayon,tech
	play=0
	clock.unschedule(prog_calculate)
	if level<3:
		readlevel(world,level,False)
	else:
		current=copy.deepcopy(worlds[world][level]['current'])
		cycle=worlds[world][level]['cycle']
		temp=worlds[world][level]['temp']
		nrj=worlds[world][level]['nrj']
		rayon=worlds[world][level]['rayon']
		erase()
		retriern()
		stat=[0,0,0,0,0,0,0,0,0]
		stat_var=[]
		if len(stat_var)==0:
			for i in range(len(statedvar)):
				stat_var.append([0])
	menus[0][1]['choose']=0
				
def reallyrun():
	global play
	play=0.15625
	clock.schedule_interval(prog_calculate,play)
	menus[0][1]['choose']=1
																			 
def retriern():
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			it=wart(x,y)	
			typetri=art[it]['nom'][:6]
			if typetri=="triern":
				acttri=""
				idtri=art[it]['nom'][8]
				if len(art[it]['nom'])==10: acttri=art[it]['nom'][9]
				world_art[x][y]=art['triern'+idtri+"-"+idtri+acttri]['value']

def swap():
	global adirection
	for dx,dy in direction:
		if random.randint(0,100)>50: 
			temps=direction[(dx,dy)][1]
			direction[(dx,dy)][1]=direction[(dx,dy)][2]
			direction[(dx,dy)][2]=temps
		if random.randint(0,100)>50: 
			temps=direction[(dx,dy)][3]
			direction[(dx,dy)][3]=direction[(dx,dy)][4]
			direction[(dx,dy)][4]=temps
		if random.randint(0,100)>50: 
			temps=direction[(dx,dy)][5]
			direction[(dx,dy)][5]=direction[(dx,dy)][6]
			direction[(dx,dy)][6]=temps
	bdirection=copy.deepcopy(adirection)
	adirection[0]=bdirection[1]
	adirection[1]=bdirection[2]
	adirection[2]=bdirection[3]
	adirection[3]=bdirection[4]
	adirection[4]=bdirection[5]
	adirection[5]=bdirection[6]
	adirection[6]=bdirection[7]
	adirection[7]=bdirection[0]
	
def gameover_ok():
	global level,world
	reallystop()
	savelevel(world,level)
	sync()
	clock.schedule_once(prog_menu,2,level)
			
def itsvictory_ok():
	global world,level,finished
	reallystop()
	finished.extend(worlds[world][level]['link'])
	finished=list(set(finished))
	savelevel(world,level)
	sync()
	clock.schedule_once(prog_menu,2,-1)
	
def gameover(x):
	global over
	over=x
	sound.queue(pyglet.resource.media("sound/gameover.mp3"))
	sound.play()
	clock.unschedule(prog_calculate)

def itsvictory():
	global over
	over=-1
	sound.queue(pyglet.resource.media("sound/victoire.mp3"))
	sound.play()
	clock.unschedule(prog_calculate)

def infos():
	global stat,sizex,sizey,cycle,thecout,victory,current
	stat=[0,0,0,0,0,0,0,0,0]
	thecout=0
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			if world_new[x][y]==art['headb2']['value']: stat[0]=stat[0]+1
			if world_new[x][y]==art['headb']['value']: stat[1]=stat[1]+1
			if world_new[x][y]==art['headp']['value']: stat[2]=stat[2]+1
			if world_new[x][y]==art['head']['value']: stat[3]=stat[3]+1
			if world_new[x][y]==art['head2']['value']: stat[4]=stat[4]+1
			if world_new[x][y]==art['headr']['value']: stat[5]=stat[5]+1
			if world_new[x][y]==art['headr2']['value']: stat[6]=stat[6]+1
			if world_new[x][y]==art['neut']['value']: stat[7]=stat[7]+1
			if world_new[x][y]==art['prot']['value']: stat[8]=stat[8]+1

			if cycle!=0: desactive(x,y)
			thecout=art[world_new[x][y]]['cout']+art[wart(x,y)]['cout']+thecout
	tempvictoire=0
	for i in range(len(victory)):
		if victory[i]-current[i]<0:
			gameover(1)
			break
		if victory[i]-current[i]>0:
			tempvictoire=tempvictoire+1000
		tempvictoire=tempvictoire+1
	if tempvictoire==len(victory): itsvictory()	
	if rayon>maxrayon: gameover(5)
	if cycle>maxcycle: gameover(6)
	if temp>maxtemp: gameover(7)
	if nrj>maxnrj: gameover(8)
	
def erase():
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			unactive(x,y)
			if world_new[x][y]==art['headp']['value'] or world_new[x][y]==art['tailp']['value']:
				world_new[x][y]=art['fiber']['value']
			elif world_new[x][y]==art['prot']['value'] or world_new[x][y]==art['neut']['value']:
				world_new[x][y]=art['nothing']['value']
			elif world_new[x][y]>=art['tail']['value']:
				world_new[x][y]=art['copper']['value']

def wart(x,y):
	return world_art[x][y] & int("0xFFFFFF",16)
	
def getactive(x,y):
	return (world_art[x][y] & int("0xFF000000",16))>>24

def isactive(x,y):
	return world_art[x][y]>int("0xFFFFFF",16)
		
def desactive(x,y):
	if world_art[x][y]>int("0x1000000",16):
		world_art[x][y]=world_art[x][y]-int("0x1000000",16)
	
def unactive(x,y):
	world_art[x][y]=world_art[x][y] & int("0x00FFFFFF",16)
		
def active(x,y):		
	world_art[x][y]=world_art[x][y] | int("0x0A000000",16)
		
def unsigned(x):
	if x>int("0xFFF",16):
		return x & int("0xF000",16)
	else:
		return x & int("0xF0",16)
	
def ispositive(x):
	if x>int("0xFFF",16):
		return x & int("0xF00",16)==int("0x100",16)
	else:
		return x & int("0xF",16)==int("0x1",16)
	
def isnegative(x):
	if x>int("0xFFF",16):
		return x & int("0xF00",16)==int("0x200",16)
	else:
		return x & int("0xF",16)==int("0x2",16)
	
def positive(x):
	if x>int("0xFFF",16):	
		return (x & int("0xF000",16))+int("0x100",16)
	else:
		return (x & int("0xF0",16))+int("0x1",16)
	
def negative(x):
	if x>int("0xFFF",16):
		return (x & int("0xF000",16))+int("0x200",16)
	else:
		return (x & int("0xF0",16))+int("0x2",16)
	
def invert(x):
	if ispositive(x):
		return negative(x)
	elif isnegative(x):
		return positive(x)
	else:
		return x
	
def isbig(x):
	return (x & int("0xF000",16))==int("0x2000",16)
	
def isgauche(n):
	return n[0]==1
	
def isdroite(n):
	return n[0]==-1

def nextgrid():
	global play,cycle,temp,rayon,nrj,current,adirection,stat,stat_var
	world_old=copy.deepcopy(world_new)
	swap()
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			value=world_old[x][y]
			flag=0
			if (wart(x,y)==art['canonh']['value'] or wart(x,y)==art['canonh2']['value']) and ((cycle%40==0 and isactive(x,y)==False) or (cycle%10==0 and isactive(x,y))):
				if world_new[x][y]>=art['head']['value']:
					gameover(4)
				elif world_new[x][y]==art['nothing']['value']:
					temp=temp+5					
				else:
					world_new[x][y]=art['head']['value']
					nrj=nrj+1
			if wart(x,y)==art['canont']['value'] and ((cycle%40==0 and isactive(x,y)==False) or (cycle%10==0 and isactive(x,y))):
				world_new[x][y]=art['tail']['value']
			if world_old[x][y] == art['headp']['value']:
				world_new[x][y]=art['tailp']['value']
			elif world_old[x][y] >= art['head']['value']:
				for dx,dy in adirection:
						if world_old[x+dx][y+dy]>=value>>8:
							break
				for ex,ey in direction[(dx,dy)]:
						if world_new[x+ex][y+ey]==art['headr']['value'] and world_new[x][y]==art['headr']['value']:
							world_old[x+ex][y+ey]=art['headr2']['value']
							world_new[x+ex][y+ey]=art['headr2']['value']
							world_new[x][y]=art['copper']['value']
							rayon=rayon+1
							break
						if world_new[x+ex][y+ey]==art['headb']['value'] and world_new[x][y]==art['headb']['value']:
							world_old[x+ex][y+ey]=art['headb2']['value']
							world_new[x+ex][y+ey]=art['headb2']['value']
							world_new[x][y]=art['copper']['value']
							rayon=rayon+1
							break
						if (world_new[x+ex][y+ey]==art['headb']['value'] and world_new[x][y]==art['headr']['value']) or (world_new[x+ex][y+ey]==art['headr']['value'] and world_new[x][y]==art['headb']['value']): 
							world_old[x+ex][y+ey]=art['copper']['value']
							world_new[x+ex][y+ey]=art['copper']['value']	
							world_new[x][y]=art['copper']['value']
							break		
						if (world_new[x+ex][y+ey]==art['headb2']['value'] and world_new[x][y]==art['headr2']['value']) or (world_new[x+ex][y+ey]==art['headr2']['value'] and world_new[x][y]==art['headb2']['value']):
							world_old[x+ex][y+ey]=art['nothing']['value']
							world_new[x+ex][y+ey]=art['nothing']['value']
							world_new[x][y]=art['nothing']['value']
							rayon=rayon+10
							break
						if world_new[x+ex][y+ey]==art['headr2']['value'] and world_new[x][y]==art['headb']['value']: 
							world_old[x+ex][y+ey]=art['headr']['value']
							world_new[x+ex][y+ey]=art['headr']['value']
							world_new[x][y]=art['copper']['value']
							rayon=rayon+1
							break
						if world_new[x+ex][y+ey]==art['headb2']['value'] and world_new[x][y]==art['headr']['value']: 
							world_old[x+ex][y+ey]=art['copper']['value']
							world_new[x+ex][y+ey]=art['copper']['value']
							world_new[x][y]=art['headr']['value']
							rayon=rayon+1
							break
						it=wart(x+ex,y+ey)
						if flag==0 and world_old[x+ex][y+ey]==art['copper']['value'] and world_new[x+ex][y+ey]<art['head']['value'] and it!=art['triern0-1']['value']  and it!=art['triern0-2']['value']  and it!=art['triern0-4']['value'] and (it!=art['triern0-4a']['value'] or isactive(x+ex,y+ey)) and (it!=art['triern0-8a']['value'] or isactive(x+ex,y+ey)) and (it!=art['trierp']['value'] or isactive(x+ex,y+ey)) and (it!=art['dir2']['value'] or isdroite((dx,dy))) and (it!=art['dir1']['value'] or isgauche((dx,dy))) and (it!=art['trierg']['value'] or isbig(value)) and (it!=art['trierr']['value'] or ispositive(value)) and (it!=art['trierb']['value'] or isnegative(value)):			
							if it==art['destroyer']['value']:
								world_new[x+ex][y+ey]=art['copper']['value']
							elif it==art['positiver']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=positive(value)
								value=positive(value)
							elif it==art['positiver2']['value']:
								world_new[x+ex][y+ey]=positive(value)
								value=positive(value)
							elif it==art['negativer']['value'] and isactive(x+ex,y+ey):				
								world_new[x+ex][y+ey]=negative(value)
								value=negative(value)
							elif it==art['inverter']['value']:			
								world_new[x+ex][y+ey]=invert(value)
								value=invert(value)
							elif it==art['neutraliser']['value']:				
								world_new[x+ex][y+ey]=unsigned(value)
								value=unsigned(value)
							elif it==art['reactor']['value'] and value==art['headr2']['value'] and isactive(x+ex,y+ey):				
								world_new[x+ex][y+ey]=art['copper']['value']
								if world_new[x+ex][y+ey-1]!=art['nothing']['value']:
									gameover(9)
								else:
									world_new[x+ex][y+ey-1]=art['prot']['value']
							elif it==art['reactor']['value'] and value==art['head2']['value'] and isactive(x+ex,y+ey):				
								world_new[x+ex][y+ey]=art['copper']['value']
								if world_new[x+ex][y+ey-1]!=art['nothing']['value']:
									gameover(9)
								else:
									world_new[x+ex][y+ey-1]=art['neut']['value']
							elif it==art['senserK']['value'] and value==art['headb']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=art['copper']['value']
								current[7]=current[7]+1
							elif it==art['senserL']['value'] and value==art['headb']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=art['copper']['value']
								current[8]=current[8]+1
							elif it==art['senserM']['value'] and value==art['headb']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=art['copper']['value']
								current[9]=current[9]+1
							elif it==art['senserN']['value'] and value==art['headb']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=art['copper']['value']
								current[10]=current[10]+1
							elif it==art['sensere']['value'] and value==art['head']['value']:
								world_new[x+ex][y+ey]=art['copper']['value']
								current[3]=current[3]+1
							elif it==art['senserf']['value'] and value==art['headr']['value']:
								world_new[x+ex][y+ey]=art['copper']['value']
								current[5]=current[5]+1
							elif it==art['senserg']['value'] and value==art['headb2']['value']:
								world_new[x+ex][y+ey]=art['copper']['value']
								current[0]=current[0]+1
							elif it==art['senserh']['value'] and value==art['head']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=art['copper']['value']
								current[3]=current[3]+1
							elif it==art['calor']['value']:				
								temp=temp-11
								world_new[x+ex][y+ey]=art['copper']['value']
							elif it==art['photonizer']['value'] and value<art['head2']['value']:		
								world_new[x+ex][y+ey]=art['copper']['value']
								for fx,fy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)):
									if world_new[x+ex+fx][y+ey+fy]==art['fiber']['value']:
										world_new[x+ex+fx][y+ey+fy]=art['headp']['value']
										break
							elif it==art['photonizer2']['value'] and value<art['head2']['value']:		
								world_new[x+ex][y+ey]=value
								for fx,fy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)):
									if world_new[x+ex+fx][y+ey+fy]==art['fiber']['value']:
										world_new[x+ex+fx][y+ey+fy]=art['headp']['value']
							else:
								world_new[x+ex][y+ey]=value
							flag=1
							typetri=art[it]['nom'][:6]
							if typetri=="triern":
								acttri=""
								numtri=int(art[it]['nom'][6])
								idtri=art[it]['nom'][8]
								if len(art[it]['nom'])==10: acttri=art[it]['nom'][9]
								if acttri=="a" and isactive(x+ex,y+ey):
									if numtri>0: numtri=numtri-1
								else:
									if numtri>0: numtri=numtri-1
								world_art[x+ex][y+ey]=art['triern'+str(numtri)+"-"+idtri+acttri]['value']
							if	it!=art['nothing']['value'] and world_new[x][y]>=art['head']['value']:
								temp=art[it]['temp']+temp
							world_new[x][y] = value>>8
							break
			elif value == art['tailp']['value']:
				world_new[x][y]=art['fiber']['value']
			elif value >= art['tail']['value'] and world_new[x][y] < art['head']['value']:
				newvalue=value-int("0x10", 16)
				if newvalue<art['tail']['value']: newvalue=art['copper']['value']
				world_new[x][y] = newvalue
			elif value == art['fiber']['value']:
				n=sum(world_old[x+dx][y+dy]==art['headp']['value'] for dx,dy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)))
				if 1 <= n <= 2:
					world_new[x][y]=art['headp']['value']
					for dx,dy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)):
						if wart(x+dx,y+dy)!=0 and art[wart(x+dx,y+dy)]['activable']==1: 
							active(x+dx,y+dy)
				else:
					art['fiber']['value']
			elif value == art['prot']['value'] or value == art['neut']['value'] :
				if wart(x,y)==art['sensern']['value'] and value==art['neut']['value'] and isactive(x,y):
					world_new[x][y]=art['nothing']['value']
					current[11]=current[11]+1
				elif wart(x,y)==art['senserp']['value'] and value==art['prot']['value'] and isactive(x,y):
					world_new[x][y]=art['nothing']['value']
					current[12]=current[12]+1
				elif world_new[x][y-1] == art['nothing']['value']:
					if y==1:
						gameover(2)
						return
					else:
						world_new[x][y-1] = value
						world_new[x][y] = art['nothing']['value']
				elif (world_new[x][y-1] == art['prot']['value'] or world_new[x][y-1] == art['neut']['value']) and world_new[x][y-1]!=world_new[x][y]:
					gameover(3)
					return
	infos()
	statedvar=[stat[0],stat[1],stat[2],stat[3],stat[4],stat[5],stat[6],stat[7],stat[8],nrj,temp,rayon,current[7],current[8],current[9],current[10],current[11],current[12]]
	for i in range(len(statedvar)):
		stat_var[i].append(statedvar[i])
		if len(stat_var[i])>100:
			stat_var[i].remove(stat_var[i][0])
	cycle=cycle+1
	
''' *********************************************************************************************** '''
''' Lancement & initialisation																							 '''
				
def main():
   pyglet.app.run()
   
win = pyglet.window.Window(width=1024, height=768,resizable=True, visible=True)
win.set_minimum_size(1024, 768)
'''win = pyglet.window.Window(fullscreen=True,resizable=True)'''

initgrid()
glEnable(GL_BLEND);
'''glEnable(GL_LINE_SMOOTH);
glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST);'''
glEnable(GL_LINE_STIPPLE)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
win.set_caption("Wirechem: The new chemistry game")
clock.schedule(prog_refresh)
player = pyglet.media.Player()
ambiance = pyglet.media.Player()
sound = pyglet.media.Player()
player.queue(pyglet.resource.media("movie/intro.mp4"))
player.play()
ambiance.queue(pyglet.resource.media("music/ambiance1.mp3"))
ambiance.play()
ambiance.volume=0.4
ambiance.eos_action='loop'
pyglet.font.add_file('font/Fluoxetine.ttf')
pyglet.font.add_file('font/OpenDyslexicAlta.otf')
pyglet.font.add_file('font/Mecanihan.ttf')
pyglet.font.add_file('font/Vademecum.ttf')
pyglet.font.add_file('font/LiberationMono-Regular.ttf')
pic_logo=image.load("picture/logo.png")
pic_logo2=image.load("picture/logo2.png")
pic_exit2=image.load("picture/exit2.png")
pic_arrows=image.load("picture/arrows.png")
pic_arrows2=image.load("picture/arrows2.png")
pic_special=image.load("picture/boss.png")	
pic_leveler=[image.load("picture/leveler0.png"),image.load("picture/leveler1.png"),image.load("picture/leveler2.png"),image.load("picture/leveler3.png"),image.load("picture/leveler4.png")]
color_leveler=[[0,192,244],[235,118,118],[5,157,60],[215,33,255],[201,209,98]]
pic_locked=image.load("picture/locked.png")
pic_cycle=image.load("picture/cycle.png")
pic_nrj=image.load("picture/nrj.png")
pic_temp=image.load("picture/temp.png")
pic_rayon=image.load("picture/rayon.png")
pic_cout=image.load("picture/cout.png")
pic_tech=image.load("picture/tech.png")
pic_test=image.load("picture/test.png")
document=pyglet.text.decode_attributed("test")
txt_description=pyglet.text.layout.TextLayout(document,dpi=72,multiline=True,width=732,height=140)
txt_description.x=8
txt_description.y=8
txt_message=pyglet.text.layout.TextLayout(document,dpi=72,multiline=True,width=384,height=200)
txt_cout2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=780,y=120,bold=False,italic=False,color=(180, 180, 180,255))
txt_obj=pyglet.text.Label("",font_name='vademecum',font_size=380,x=0,y=0,bold=False,italic=False,color=(255, 80, 80,230))
txt_maxcycle2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=780,y=75,bold=False,italic=False,color=(180, 180, 180,255))
txt_tech2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=980,y=120,bold=False,italic=False,color=(180, 180, 180,255))
txt_maxrayon2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=970,y=75,bold=False,italic=False,color=(180, 180, 180,255))
txt_maxtemp2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=875,y=120,bold=False,italic=False,color=(180, 180, 180,255))
txt_maxnrj2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=875,y=75,bold=False,italic=False,color=(180, 180, 180,255))
txt_element2=pyglet.text.Label("",font_name='Vademecum',font_size=23,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_nom2=pyglet.text.Label("",font_name='Fluoxetine',font_size=18,x=0,y=0,bold=False,italic=False,color=(255, 255, 255,255))
txt_victory1=pyglet.text.Label("",font_name='Mechanihan',font_size=25,x=0,y=0,bold=False,italic=False,color=(255, 255, 255,255))
txt_victory2=pyglet.text.Label("",font_name='Mechanihan',font_size=10,x=0,y=0,bold=False,italic=False,color=(255, 255, 255,255))
txt_element=pyglet.text.Label("",font_name='vademecum',font_size=23,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_item=pyglet.text.Label("",font_name='Liberation Mono',font_size=2,x=0,y=0)
txt_stat=pyglet.text.Label("",font_name='Mechanihan',font_size=24,x=0,y=0,bold=False,italic=False,color=(255, 255, 255,255))
txt_cout=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=0,y=18,bold=False,italic=False,color=(180, 180, 180,255))
txt_tech=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=0,y=18,bold=False,italic=False,color=(180, 180, 180,255))
txt_over=pyglet.text.Label("",font_name='Mechanihan',font_size=100,x=win.width/2-350,y=win.height/2-200,color=(255,255,255,255))
txt_over2=pyglet.text.Label("",font_name='Mechanihan',font_size=30,x=0,y=win.height/2-90,color=(255,255,255,255))
txt_drag=pyglet.text.Label("",font_name='Mechanihan',font_size=14,x=950,y=win.height-20,color=(255,255,255,255))
txt_temp=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_son=pyglet.text.Label("Reglages du son",font_name='Mechanihan',font_size=30,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_video=pyglet.text.Label("Options Video",font_name='Mechanihan',font_size=30,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))

''' *********************************************************************************************** '''
''' Fonctions liees aux menus																								 '''

def click_sound(state):
	print "sound"
	
def click_nosound(state):
	print "nosound"
	
def click_settings(state):
	global level,world
	reallystop()
	savelevel(world,level)
	sync()
	level=-2
	
def click_loadit(state):
	global users,world_art,world_new,world,level
	if state['j']==1:
		readlevel(world,level,False)
	else:
		world_new=copy.deepcopy(users[len(users)-state['j']+1][1])
		world_art=copy.deepcopy(users[len(users)-state['j']+1][2])
				
def click_load(state):
	global menus,savenames,users
	if menus[2][0]['visible']:
			menus[2][0]['visible']=False
			return
	if len(menus[2])<=1:
		menus[2].append({'click': 'click_loadit', 'motion':'motion_popup', 'tech':1, 'value':'Version originale', 'size':0, 'icon': {'color': [255, 100, 100], 'text': '#', 'activable': False},'active':True,'variable':True,'visible':True,'separe':True,'squarred':False})
		for i in range(len(savenames)):
				menus[2].append({'click': 'click_loadit', 'motion':'motion_popup', 'tech':1, 'value':'#users[len(users)-'+str(i)+'-1][0].strftime("%Y-%m-%d %H:%M")', 'size':0, 'icon': {'color': [255, 255, 255], 'colorise':True,  'text': savenames[i], 'activable': False},'active':'len(users)>'+str(i),'variable':True,'visible':True,'separe':False,'squarred':False})
	menus[2][0]['visible']=True
		
def click_save(state):
	global world_art,world_dat,world,level,users
	users.append([datetime.datetime.now(),copy.deepcopy(world_new),copy.deepcopy(world_art)])
	savelevel(world,level)
	sync()
	
def click_speed(state):
	global play,zoom
	if state.has_key('-'):
		play=float(play)*2
	else:
		play=float(play)/2
	if play>=5:
		play=0.01953125
	if play<0.01953125:
		play=2.5
	clock.unschedule(prog_calculate)
	clock.schedule_interval(prog_calculate,play)
	
def click_choose(state):
	menus[0][18]['icon']=copy.deepcopy(menus[3][state['j']]['value'])

def click_drag_transmuter(state):
	global tech,menus
	if state['onmenu']:
		if menus[3][0]['visible']:
			menus[3][0]['visible']=False
			return
		if len(menus[3])<=1:
			for i in range(196608,196637):
				menus[3].append({'click': 'click_choose', 'motion':'motion_popup', 'tech':art[i]['tech'], 'value':art[i], 'size':0, 'icon':art[i],'active':True,'variable':True,'visible':True,'separe':False,'squarred':False})
		menus[3][0]['visible']=True
		return
	if state['realx']>=1 and state['realy']>=1 and state['realx']<sizex-1 and state['realy']<sizey-1 and play==0 and (world_art[state['realx']][state['realy']]==0 or art[world_art[state['realx']][state['realy']]]['tech']<tech):
		value=menus[0][18]['icon']['value']
		if value==art['null']['value']:
			value=art['nothing']['value']
		if world_new[state['realx']][state['realy']]!=art['fiber']['value'] and world_new[state['realx']][state['realy']]<art['tail']['value']: 
			if cout-thecout-menus[0][18]['icon']['cout'] >= 0:
				world_art[state['realx']][state['realy']] = value
				infos()

def click_nothing(state):
	state()
	
def click_drag_nothing(state):
	global tech
	if state['realx']>=1 and state['realy']>=1 and state['realx']<sizex-1 and state['realy']<sizey-1 and play==0:
		if world_art[state['realx']][state['realy']] == art['nothing']['value']:
			world_new[state['realx']][state['realy']] = art['nothing']['value']				
		elif art[world_art[state['realx']][state['realy']]]['tech']<=tech:
			world_art[state['realx']][state['realy']] = art['nothing']['value']
		infos()
		
def click_drag_copper(state):
	if state['realx']>=1 and state['realy']>=1 and state['realx']<sizex-1 and state['realy']<sizey-1 and play==0:
		if world_new[state['realx']][state['realy']]<art['tail']['value']: 
			if cout-thecout-art['copper']['cout'] >= 0:
				world_new[state['realx']][state['realy']] = art['copper']['value']
				infos()
	
def click_drag_fiber(state):
	if state['realx']>=1 and state['realy']>=1 and state['realx']<sizex-1 and state['realy']<sizey-1 and play==0:
		if world_art[state['realx']][state['realy']]==0 and world_new[state['realx']][state['realy']]<art['tail']['value']: 
			if cout-thecout-art['fiber']['cout'] >= 0:
				world_new[state['realx']][state['realy']]=art['fiber']['value']
				infos()
				
def click_tutoriel(state):
	print "tuto"

def click_popup(state):
	print "popup"	
	
def click_simple(state):
	print "simple"	
		
def click_menu(state):
	global level,world
	reallystop()
	savelevel(world,level)
	sync()
	level=-1

def click_exit(state):
	global level,world
	if level>=0:
		savelevel(world,level)
		sync()
	pyglet.app.exit()
	
def click_stat(state):
	global seestat
	if seestat>3:
		seestat=0
	else:
		seestat=seestat+1
	resize()
		
def click_stop(state):
		reallystop()
		
def click_run(state):
		reallyrun()
		
def drag_move(state):
	global decx,decy
	decx=decx+state['dx']
	decy=decy+state['dy']
	
def click_fullscreen(state):
	win.set_fullscreen(fullscreen=True)
	resize()
	
def click_windowed(state):
	win.set_fullscreen(fullscreen=False)
	resize()
		
def click_zoomm(state):
	global zoom,decx,decy
	decx=decx+2*state['realx']
	decy=decy+2*state['realy']
	zoom=zoom-2
	
def click_zoomp(state):
	global zoom,decx,decy
	decx=decx-2*state['realx']
	decy=decy-2*state['realy']
	zoom=zoom+2
	
def motion_popup(state):
	global allcout,menus
	if menus[0][12]['choose']==0: return
	allcout[0]=state['x']
	allcout[1]=state['y']	
	if type(menus[state['i']][state['j']]['value']) is list:
		allcout[2]=menus[state['i']][state['j']]['value'][menus[state['i']][state['j']]['choose']]
	else:
		allcout[2]=menus[state['i']][state['j']]['value']
	if type(allcout[2]) is str and allcout[2][0]=="#":
		allcout[2]=eval(allcout[2][1:])

''' *********************************************************************************************** '''
''' Fonctions liée à la gestion des menus  															'''

def launch(x,y,dx,dy,i,j,buttons,modifiers,onmenu):
	global menus,decx,decy,zoom,tuto,debug
	realx=(x-decx)/zoom
	realy=(y-decy)/zoom
	state={'x':x,'y':y,'realx':realx, 'realy':realy, 'dx':dx, 'dy':dy, 'i':i, 'j':j, 'buttons':buttons, 'modifiers':modifiers, 'onmenu': onmenu}
	if buttons==0: 
		state['event']='motion'
	else:
		if dx==0 and dy==0:
			state['event']='click'
		else:
			state['event']='drag'
	if debug: print state
	if onmenu and state['event']=='click' and menus[i][0]['selectable']:
		menus[i][0]['mouse'][buttons-1]=j
	if tuto!='' and tuto[1]<len(tuto[0]): 
		cmd,arg=tuto[0][tuto[1]]
		if cmd=='wait':
			if arg[0].lower()==state['event']:
				if buttons==int(arg[1]) or (len(arg)==1 and arg[1]=='' and int(arg[1])==0):
					tuto[1]+=1
					clock.schedule_once(execute,0.1)			
			elif arg[0].lower()=='menu':
				if buttons==int(arg[1]) or (len(arg)==1 and arg[1]=='' and int(arg[1])==0):
					tuto[1]+=1
					clock.schedule_once(execute,0.1)	
			else:
				if state['event']=='click' and arg[0]=='':
					tuto[1]+=1
					clock.schedule_once(execute,0.1)
					return				
	if menus[i][j].has_key(state['event']):
		if type(menus[i][j][state['event']]) is list:
			if callable(eval(menus[i][j][state['event']][menus[i][j]['choose']])): 
				choosed=menus[i][j]['choose']
				if state['event']=='click':
					menus[i][j]['choose']+=1
					if menus[i][j]['choose']>=len(menus[i][j]['click']):
						menus[i][j]['choose']=0
				eval(menus[i][j][state['event']][choosed]+"("+str(state)+")")
				return True
		else:
			if callable(eval(menus[i][j][state['event']])): 
				eval(menus[i][j][state['event']]+"("+str(state)+")")
				return True
	return False
			
def testmenu(themenus,x,y,dx,dy,buttons,modifiers):
	global tech
	allcout[2]=0
	for i in range(len(themenus)):
		if themenus[i][0]['visible']:
			if themenus[i][0]['place']=='bottom':
				placey=8
			elif themenus[i][0]['place']=='top':
				placey=win.height-themenus[i][0]['size']+8
			else:
				for search in themenus:
					if search[0]['place']=='bottom':
						placey=search[0]['size']+8
						break
			placex=0
			for j in range(1,len(themenus[i])):
				if themenus[i][j]['size']<30: continue
				if type(themenus[i][j]['visible']) is str and not eval(themenus[i][j]['visible']) or not themenus[i][j]['visible']: continue
				if themenus[i][j]['tech']>tech or not ((type(themenus[i][j]['active']) is str and eval(themenus[i][j]['active'])) or (type(themenus[i][j]['active']) is not str and themenus[i][j]['active'])): 
					placex+=themenus[i][j]['size']
					continue
				if x>placex and x<placex+themenus[i][j]['size'] and y>placey and y<placey+themenus[i][0]['size']-8:
					return launch(x,y,dx,dy,i,j,buttons,modifiers,True)
				placex+=themenus[i][j]['size']
	return

def testgrid(themenus,x,y,dx,dy,buttons,modifiers):
	for i in range(len(themenus)):
		if themenus[i][0]['visible'] and themenus[i][0]['selectable'] and themenus[i][0].has_key('mouse'):
			if buttons>0:
				launch(x,y,dx,dy,i,themenus[i][0]['mouse'][buttons-1],buttons,modifiers,False)
				
					
''' *********************************************************************************************** '''
''' Fonctions tutoriel			
																	 '''
def compiler():
	global tuto
	tutoexec=tuto.splitlines(False)
	result=[]
	for line in tutoexec:
		clock.tick()
		if line=='': continue
		cmd=line.split(" ")[0].lower()
		arg=line[len(cmd):].lstrip().split(',')
		for i in range(len(arg)):
			arg[i]=arg[i].lstrip().rstrip()
		result.append((cmd,arg))
	tuto=[result,0]
						
def execute(dummy):
	global tuto,rect,tech,msg,menus
	dt=0.001
	if tuto=='' or tuto[1]>=len(tuto[0]): return
	cmd,arg=tuto[0][tuto[1]]
	if debug: print cmd,arg
	if cmd=='rect':
		rect=[int(arg[0]),int(arg[1]),int(arg[2]),int(arg[3]),0]
	elif cmd=='wait':
		if len(arg)==1 and arg[0]!='' and int(arg[0])>0: 
			dt=int(arg[0])
		else:
			dt=0
	elif cmd=='next':
		nextgrid()
	elif cmd=='del':
		rect=0
		msg=''
	elif cmd=='tech':
		tech= int(arg[0])
	elif cmd=='msg':
		msg= str(arg[0].replace(';',','))
	elif cmd=='select':
		if menus[int(arg[0])][0].has_key('mouse'):
			menus[int(arg[0])][0]['mouse'][int(arg[2])]=int(arg[1])
	elif cmd=='set':
		menus[int(arg[0])][int(arg[1])]['squarred']=True
	elif cmd=='unset':
		menus[int(arg[0])][int(arg[1])]['squarred']=False
	elif cmd=='arrow':
		rect=[int(arg[0]),int(arg[1]),int(arg[2]),int(arg[3]),1]
	elif cmd=='menu':
		launch(0,0,0,0,int(arg[0]),int(arg[1]),int(arg[2]),0,True)
	elif cmd=='click':
		launch(int(arg[0]),int(arg[1]),0,0,0,0,int(arg[2]),0,False)
	elif cmd=='drag':
		launch(int(arg[0]),int(arg[1]),int(arg[2])-int(arg[0]),int(arg[3])-int(arg[1]),0,0,int(arg[4]),0,False)
	if dt!=0: 
		clock.schedule_once(execute,dt)
		tuto[1]+=1

''' *********************************************************************************************** '''
''' Fonctions evenementielles																	 '''
				
@win.event
def on_key_press(symbol, modifiers):
	global play,over,level
	if tuto!='' and tuto[1]<len(tuto[0]): 
		cmd,arg=tuto[0][tuto[1]]
		if cmd=='wait' and len(arg)==1 and arg[0]=='':
			tuto[1]+=1
			clock.schedule_once(execute,0.1)				
	if player.source and player.source.video_format:
		player.next()
		ambiance.play()
		return
	if over>0: 
		gameover_ok()
		return
	if over<0: 
		itsvictory_ok()
		return
	if level<0: return
	if symbol==key.SPACE:
		nextgrid()
	if symbol==key.BACKSPACE:
		erase()
	elif symbol==key.RETURN:
		if play>0:
			reallystop()
		else:
			reallyrun()
	elif symbol==key.NUM_SUBTRACT:
		click_speed({'-':True})
	elif symbol==key.NUM_ADD:
		click_speed({'+':True})

@win.event	
def on_mouse_motion(x, y, dx, dy):
	global world,selected,allcout,over,level,worlds,finished,users,menus
	selected=-1
	for l in range(len(worlds[world])):
		ele=worlds[world][l]
		if x>ele['_xx']+20 and x<ele['_xx']+100 and y>ele['_yy']/768.0*win.height+0 and y<ele['_yy']/768.0*win.height+110 and ((world,l) in finished):
			selected=ele
	if x>940 and y>win.height-100 and x<1024 and y<win.height:
		selected=-2
	if x>840 and y>150 and x<920 and y<240:
		selected=-3
	if x>920 and y>150 and x<1024 and y<240:
		selected=-4	
	if level<0: return
	testmenu(menus,x,y,dx,dy,0,0)
				
@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global zoom,over,level,menus
	if player.source and player.source.video_format:
		player.next()
		ambiance.play()
		return
	if over>0: 
		gameover_ok()
		return
	if over<0: 
		itsvictory_ok()
		return
	if level<0: return	
	testgrid(menus,x,y,dx,dy,[mouse.LEFT,mouse.MIDDLE,mouse.RIGHT].index(buttons)+1, modifiers)
	
@win.event
def on_mouse_press(x, y, button, modifiers):
	global zoom,over,level,selected,world,users,world_new,world_art,menus,tuto
	if player.source and player.source.video_format:
		player.next()
		ambiance.play()
		return
	if over>0: 
		gameover_ok()
		return
	if over<0: 
		itsvictory_ok()
		return
	if level<0:
		if selected==-2:
			pyglet.app.exit()
		elif selected==-4:
			if world>0:	world=world-1
		elif selected==-3:
			if world<len(worlds)-1: world=world+1
		elif selected==-1:		
			return
		else:
			'''readlevel(selected['world'],selected['level'],True)'''
			readlevel(selected['world'],selected['level'],False)
			if video:
				player.queue(pyglet.resource.media('movie/level'+str(world)+"-"+str(level)+".mp4"))
				player.play()
				ambiance.pause()
				selected=-1
			if type(tuto) is str and tuto!='':
				compiler()
				execute(0)
		return
	if not testmenu(menus,x,y,0,0,[mouse.LEFT,mouse.MIDDLE,mouse.RIGHT].index(button)+1,modifiers):
		testgrid(menus,x,y,0,0,[mouse.LEFT,mouse.MIDDLE,mouse.RIGHT].index(button)+1, modifiers)
	
@win.event
def on_resize(width,height):
	resize()

if __name__ == '__main__':
    main()
