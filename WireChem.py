#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import pyglet
import copy
import csv
import random
import time
import operator
import shelve
import os
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
		
def interprete(d):
	for k in d.keys():
		if 'icon' in d[k]:
			print d[k]
			if type(d[k]['icon']) is str and len(d[k]['icon'])>0 and d[k]['icon'][0]=="%":
				d[k]['icon']=image.load(d[k]['icon'][1:])	
			
def initgrid():
	global art,Uworlds,statedvar,stat_var,seestat,adirection,worlds,finished,allcout,selected,world,level,over,mousel,mouser,mousem,sizex,sizey,world_old,world_new,world_art,dat,direction,zoom,play,stat,cycle,cout,thecout,rayon,unroll,debug,temp,decx,decy,nrj,tech,victory,current,maxnrj,maxrayon,maxcycle,maxtemp,nom,descriptif,element
	
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
	
	verifyhome()
	read("dbdata")
	read(gethome()+"/dbdata")
	reference(worlds,['world','level'])
	reference(Uworlds,['world','level'])
	duplicateref(art)
	duplicateref(dat)
	interprete(dat)	
	''' Variables globales '''
	zoom=25
	stat=[0,0,0,0,0,0,0,0,0]
	nom=descriptif=element='H'
	victory=[0,0,0,0,0,0,0,0,0,0,0,0,0]
	current=[0,0,0,0,0,0,0,0,0,0,0,0,0]
	stat_var=[]
	mousel=4
	mouser=0
	mousem=3
	maxnrj=maxrayon=maxcycle=maxtemp=99999
	allcout=[0,0,0]
	sizex=sizey=1
	seestat=thecout=world=over=play=cycle=rayon=temp=cout=decx=decy=unroll=nrj=0
	debug=1
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


''' *********************************************************************************************** '''
''' Sauvegarde/Restauration																								 '''
					
def resize():
	global zoom,decx,decy,seestat
	if seestat>=1:
		allsizex=2*win.width/3
	else:
		allsizex=win.width
	if sizex/float(sizey)<allsizex/(win.height-102.0):
		zoom=(win.height-102)/(sizey-2)
	else:
		zoom=allsizex/(sizex-2)
	decx=-zoom+(allsizex-zoom*(sizex-2))/2
	decy=-zoom+(win.height-zoom*(sizey-2))/2

def readlevel(w,l,user):
	global worlds,unroll,mousel,mousem,mouser,cout,selected,sizex,sizey,unroll,stat,debug,tech
	if user:
		if w<len(Uworlds) and l<len(Uworlds[w]) and Uworlds[w][l].has_key("element"):
			load(Uworlds[w][l])
		else:
			load(worlds[w][l])
	else:
		load(worlds[w][l])
	if debug==1: tech=9
	if tech<0:
		dat['setcopper']['value']='setnothinga'
		dat['setfiber']['value']='setnothinga'
		dat['setnothing']['value']='setnothinga'
		dat['others']['value']='setnothinga'
	elif tech<2:
		dat['setcopper']['value']='setcopper'
		dat['setfiber']['value']='setnothinga'
		dat['setnothing']['value']='setnothing'
		dat['others']['value']='others'
	else:
		dat['setcopper']['value']='setcopper'
		dat['setfiber']['value']='setfiber'
		dat['setnothing']['value']='setnothing'
		dat['others']['value']='others'	
	sizex=len(world_new)
	sizey=len(world_new[0])
	resize();	
	stat=[0,0,0,0,0,0,0,0,0]
	unroll=over=0
	infos()

	
def savelevel(w,l):
	global worlds,Uworlds,nom,descriptif,video,link,tech,cout,victory,current,cycle,nrj,rayon,temp,maxcycle,maxnrj,maxrayon,maxtemp,world_new,world_art
	while len(Uworlds)<=w:
		Uworlds.append(0)
		Uworlds[w]=[]
	while len(Uworlds[w])<=l:
		Uworlds[w].append({})
	Uworlds[w][l]={'nom':nom, 
'element':element,
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

def  menu(dt,leveler):
	global level,over
	level=leveler
	over=0
		
def calculate(dt):
	nextgrid()
	
def refresh(dt):
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
		if it['activable']:
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
	drawsquare(x,y,x2,y2,0,[90,90,90])
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
	global selected,victory,finished,world,level
	drawsquare(740,148,1016,8,1,[40,40,40])
	drawsquare(8,148,1016,8,0,[90,90,90])
	glColor3ub(255,255,255)
	pic_logo.blit(185,win.height-200)
	pic_logo2.blit(45,win.height-160)
	txt_world.x=20
	txt_world.y=win.height-50
	txt_world.text="Labo "+str(world+1)
	txt_world.draw()
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
					drawLaser(ele['_xx']+50,int(ele['_yy']/768.0*win.height+50),worlds[n[0]][n[1]]['_xx']+50,int(worlds[n[0]][n[1]]['_yy']/768.0*win.height+50),random.randint(0,6),20,[0,100,0],12)	
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
				dat['cout']['icon'].blit(740,110)
				txt_cout2.text=str(ele['cout'])
				txt_cout2.draw()
			if ele['maxcycle']<90000:
				dat['cycle']['icon'].blit(740,65)
				txt_maxcycle2.text=str(ele['maxcycle'])
				txt_maxcycle2.draw()
			if ele['tech']>0:	
				dat['tech']['icon'].blit(940,110)
				txt_tech2.text=str(ele['tech'])
				txt_tech2.draw()
			if ele['maxrayon']<90000:	
				dat['rayon']['icon'].blit(940,65)
				txt_maxrayon2.text=str(ele['maxrayon'])
				txt_maxrayon2.draw()
			if ele['maxtemp']<90000:	
				dat['temp']['icon'].blit(850,110)
				txt_maxtemp2.text=str(ele['maxtemp'])
				txt_maxtemp2.draw()
			if ele['maxnrj']<90000:	
				dat['nrj']['icon'].blit(850,65)
				txt_maxnrj2.text=str(ele['maxnrj'])
				txt_maxnrj2.draw()
			victory=ele['victory']
			drawcondvictory(742,12,1016,50,[40,40,40])
			glColor3ub(255,0,0)
		pic_levels2.blit(ele['_xx'],ele['_yy']/768.0*win.height)
		glColor3ub(255,255,255)
		if (world,l) not in finished:
			pic_locked.blit(ele['_xx']+10,ele['_yy']/768.0*win.height+10)
		txt_element2.text=ele['element']
		txt_element2.x=ele['_xx']+50
		txt_element2.y=ele['_yy']/768.0*win.height+67
		txt_element2.color=(int(ele['_xx']/1024.0*150), int(ele['_xx']/1024.0*150), int(ele['_xx']/1024.0*150),255)
		txt_element2.draw()
		calc=(len(ele['nom'])*17-52)/2
		drawsquare(ele['_xx']+35-calc,int(ele['_yy']/768.0*win.height+2),ele['_xx']+42-calc+len(ele['nom'])*17,int(ele['_yy']/768.0*win.height-18),1,[40,int(ele['_xx']/1024.0*135),int(ele['_xx']/1024.0*100)])			
		txt_nom2.text=ele['nom'].decode('utf-8')
		txt_nom2.x=ele['_xx']+38-calc
		txt_nom2.y=ele['_yy']/768.0*win.height-15
		txt_nom2.color=acolor
		txt_nom2.draw()
			
def calc_space(nb,nbtot):
	global unroll
	return [2*win.width/3+20,(nb-1)*(win.height-100-unroll*50)/nbtot+50+unroll*50+20,win.width-20,nb*(win.height-100-unroll*50)/nbtot+50+unroll*50]

def drawpopup():
	global allcout
	if tech<6:
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+75,1,[40,40,40])
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+75,0,[255,255,255])
	else:
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+150,1,[40,40,40])
		drawsquare(allcout[0],allcout[1],allcout[0]+90,allcout[1]+150,0,[255,255,255])
	txt_drag.x=allcout[0]+45
	txt_drag.y=allcout[1]+10
	glColor3ub(255,255,255,255)
	dat['cout']['icon'].blit(allcout[0]+2,allcout[1]+2)
	txt_drag.text=str(allcout[2]['cout'])
	txt_drag.draw()
	txt_drag.x=allcout[0]+45
	txt_drag.y=allcout[1]+45
	glColor3ub(255,255,255,255)
	dat['tech']['icon'].blit(allcout[0]+2,allcout[1]+37)
	txt_drag.text=str(allcout[2]['tech'])
	txt_drag.draw()
	if tech>6:
		txt_drag.x=allcout[0]+45
		txt_drag.y=allcout[1]+80
		glColor3ub(255,255,255,255)
		dat['nrj']['icon'].blit(allcout[0]+2,allcout[1]+72)
		txt_drag.text=str(allcout[2]['nrj'])
		txt_drag.draw()	
		txt_drag.x=allcout[0]+45
		txt_drag.y=allcout[1]+115
		glColor3ub(255,255,255,255)
		dat['temp']['icon'].blit(allcout[0]+2,allcout[1]+107)
		txt_drag.text=str(allcout[2]['temp'])
		txt_drag.draw()	

def drawbigstat(page):	
	global unroll,stat_var	
	drawsquare(2*win.width/3,50+unroll*50,win.width,win.height-50,1,[40,40,40])
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
		dat['nrj']['icon'].blit(coord[0],coord[1])
		coord=calc_space(2,3)
		drawgraph(coord,stat_var[10],1,[180,180,180])
		dat['temp']['icon'].blit(coord[0],coord[1])
		coord=calc_space(3,3)
		drawgraph(coord,stat_var[11],1,[180,180,180])
		dat['rayon']['icon'].blit(coord[0],coord[1])
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
	
def drawgrid(zoom):
	global temp,debug,over,allcout,play,element,seestat,art
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
	drawsquare(0,win.height,win.width,win.height-50,1,[40,40,40])
	drawsquare(0,50,win.width,0,1,[40,40,40])
	if unroll!=0:	
		if debug==1:
			nbelements=44
		else:
			nbelements=29
		size=win.width/nbelements	
		drawsquare(0,57+size,win.width,0,1,[40,40,40])
		cat=65555
		for i in range(nbelements):
			it=art[int("0x30000",16)+i]
			if it['tech']<=tech: 
				drawitem(10+i*size,55,art[int("0x30000",16)+i],size-6,10)
				if it['cat']!=cat:
					drawsquare(7+i*size,55,8+i*size,55+size,0,[90,90,90])         
					cat=it['cat']
	drawsquare(win.width-409,win.height-45,win.width-369,win.height-5,1,[240,int(worlds[world][level]['_xx']/1024.0*120+100), int(worlds[world][level]['_xx']/1024.0*120+100)])
	txt_element.text=element
	txt_element.color=(int(worlds[world][level]['_xx']/1024.0*150),int(worlds[world][level]['_xx']/1024.0*150), int(worlds[world][level]['_xx']/1024.0*150),255)
	txt_element.x=win.width-384-len(element)*10
	txt_element.y=win.height-38
	txt_element.draw()
	addx=(win.width-1024)/4
	if addx<0: addx=0
	for i in range(4):
		if (i==0 and tech>0) or (i==1 and tech>6) or (i==2 and tech>7) or (i==3 and tech>8):
			glColor3ub(255,255,255)
			dat[int("0x10000",16)+i]['icon'].blit(10+i*(150+addx),win.height-45)
			if (tech>=5 and addx>100):
				txt_temp.text=str(eval(dat[int("0x10000",16)+i]['nom']))
				txt_temp.x=50+i*(150+addx)
				txt_temp.y=y=win.height-38
				txt_temp.color=(180, 180, 180,255)
				txt_temp.font_size=24
				txt_temp.draw()
				txt_temp.text="/"+str(eval("max"+dat[int("0x10000",16)+i]['nom']))
				if txt_temp.text=="/99999": txt_temp.text="/illimité".decode('utf-8')
				txt_temp.x=150+i*(150+addx)
				txt_temp.y=win.height-38
				txt_temp.color=(110, 110, 110,255)
				txt_temp.font_size=12
				txt_temp.draw()
			elif (tech>=5):
				txt_temp.text=str(eval(dat[int("0x10000",16)+i]['nom']))
				txt_temp.x=50+i*(150+addx)
				txt_temp.y=win.height-29
				txt_temp.color=(180, 180, 180,255)
				txt_temp.font_size=24
				txt_temp.draw()
				txt_temp.text=str(eval("max"+dat[int("0x10000",16)+i]['nom']))
				if txt_temp.text=="99999": txt_temp.text="illimité".decode('utf-8')
				txt_temp.x=50+i*(150+addx)
				txt_temp.y=win.height-47
				txt_temp.color=(110, 110, 110,255)
				txt_temp.font_size=12
				txt_temp.draw()
			else:
				txt_temp.text=str(eval(dat[int("0x10000",16)+i]['nom']))
				txt_temp.x=50+i*(150+addx)
				txt_temp.y=y=win.height-38
				txt_temp.color=(180, 180, 180,255)
				txt_temp.font_size=24
				txt_temp.draw()
	drawcondvictory(win.width-364,win.height-45,1020,win.height-5,[90,90,90])
	for i in range(15):
		glColor3ub(255,255,255)
		if dat[int("0x20000",16)+i]['icon']=="/":
			drawitem(10+i*45,8,dat[int("0x20000",16)+i]['ref'],36,10)
		elif dat[int("0x20000",16)+i]['icon']!="":
			dat[int("0x20000",16)+i]['icon'].blit(10+i*45,8)
		else:
			drawsquare(10+i*45,8,46+i*45,44,1,dat[int("0x20000",16)+i]['color'])
		if i==11 or i==6:
			drawsquare(5+i*45,8,6+i*45,44,0,[90,90,90])
		if i==1:
			drawsquare(45+i*45,8,49+i*45,44,1,[0,0,0])
			drawsquare(45+i*45,8,49+i*45,44*10*len(str(play))/100,1,[255,0,0])	
		if (mousel==i):
			selectcolor=[255,0,0,40] 
		elif (mouser==i):
			selectcolor=[0,255,0,40]  
		elif (mousem==i):
			selectcolor=[0,0,255,40] 
		else:
			selectcolor=[40,40,40,0]
		if play>0 and ((mousem==i) or (mousel==i) or (mouser==i)):
			glLineWidth(random.randint(1,3))
			glLineStipple(random.randint(0,10),random.randint(0,65535))	
		drawsquare(10+i*45,8,46+i*45,44,2,selectcolor)
		if play>0 and ((mousem==i) or (mousel==i) or (mouser==i)):
			glLineStipple(random.randint(0,10),random.randint(0,65535))
		drawsquare(9+i*45,7,47+i*45,45,2,selectcolor)
		glLineStipple(0,65535)
		glLineWidth(1)
	drawsquare(5+15*45,8,6+15*45,44,0,[90,90,90])
	posx=10+15*45
	addx=171+win.width-1024
	if addx<500:
		drawstat(posx,8,posx+addx,44,[stat[0],stat[1],stat[3],stat[4],stat[5],stat[6],stat[2],stat[7],stat[8]],[art['headb2']['color'],art['headb']['color'],art['head']['color'],art['head2']['color'],art['headr']['color'],art['headr2']['color'],art['headp']['color'],art['neut']['color'],art['prot']['color']])
	else:
		drawstat(posx,8,posx+(addx-20)/2,44,[stat[0],stat[1],stat[3],stat[4],stat[5],stat[6]],[art['headb2']['color'],art['headb']['color'],art['head']['color'],art['head2']['color'],art['headr']['color'],art['headr2']['color']])
		drawstat(posx+(addx-20)/2+20,8,posx+addx,44,[stat[2],stat[7],stat[8]],[art['headp']['color'],art['neut']['color'],art['prot']['color']])
	if tech>=0:	
		glColor3ub(255,255,255)
		dat['cout']['icon'].blit(posx+addx+4,7)
		txt_cout.text=str(cout-thecout)
		if (cout-thecout)>0:
			txt_cout.x=posx+addx+44
			txt_cout.color=(180, 180, 180,255)
		else:
			txt_cout.color=(255, 0, 0,255)
		txt_cout.draw()
	if tech>0:
		glColor3ub(255,255,255)
		dat['tech']['icon'].blit(posx+addx+109,7)
		txt_tech.x=posx+addx+144
		txt_tech.text=str(tech)
		txt_tech.draw()
	if seestat>=1: drawbigstat(seestat)
	if over>0: drawgameover()
	if over<0: drawvictory()
	if allcout[2]>0: drawpopup()
		
''' *********************************************************************************************** '''
''' Fonctions liees aux menus																								 '''

def settings(dummy1,dummy2,dummy3,dummy4):
	global level,world
	reallystop()
	savelevel(world,level)
	sync()
	level=-2
				
def raz(dummy1,dummy2,dummy3,dummy4):
	readlevel(world,level,False)
	
def speed(x,y,dummy1,dummy2):
	global play,zoom
	if x==1980 and y==2:
		play=float(play)*2
	else:
		play=float(play)/2
	if play>=5:
		play=0.01953125
	if play<0.01953125:
		play=2.5
	clock.unschedule(calculate)
	clock.schedule_interval(calculate,play)

def others(x,y,dummy1,dummy2):
	global tech
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0 and (world_art[x][y]==0 or art[world_art[x][y]]['tech']<tech):
		value=dat['others']['ref']['value']
		if value==art['null']['value']:
			value=art['nothing']['value']
		if world_new[x][y]!=art['fiber']['value'] and world_new[x][y]<art['tail']['value']: 
			if cout-thecout-dat['others']['ref']['cout'] >= 0:
				world_art[x][y] = value
				infos()

def setnothinga(x,y,dummy1,dummy2):
	infos()
	
def setnothing(x,y,dummy1,dummy2):
	global tech
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		if world_art[x][y] == art['nothing']['value']:
			world_new[x][y] = art['nothing']['value']				
		elif art[world_art[x][y]]['tech']<=tech:
			world_art[x][y] = art['nothing']['value']
		infos()
		
def setcopper(x,y,dummy1,dummy2):
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		if world_new[x][y]<art['tail']['value']: 
			if cout-thecout-art['copper']['cout'] >= 0:
				world_new[x][y] = art['copper']['value']
				infos()
	
def setfiber(x,y,dummy1,dummy2):
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		if world_art[x][y]==0 and world_new[x][y]<art['tail']['value']: 
			if cout-thecout-art['fiber']['cout'] >= 0:
				world_new[x][y]=art['fiber']['value']
				infos()
		
def levels(dummy1,dummy2,dummy3,dummy4):
	global level,world
	reallystop()
	savelevel(world,level)
	sync()
	level=-1

def exits(dummy1,dummy2,dummy3,dummy4):
	if level>=0:
		savelevel(world,level)
		sync()
	pyglet.app.exit()
	
def stater(dummy1,dummy2,dummy3,dummy4):
	global seestat
	if seestat>3:
		seestat=0
	else:
		seestat=seestat+1
	resize()
		
def stop(dummy1,dummy2,dummy3,dummy4):
	global play
	if play>0:
		reallystop()
	else:
		reallyrun()
		
def run(dummy1,dummy2,dummy3,dummy4):
	global play
	if play>0:
		reallystop()
	else:
		reallyrun()
		
def move(dummy1,dummy2,dx,dy):
	global decx,decy
	decx=decx+dx
	decy=decy+dy
	
def screen(dummy1,dummy2,dummy3,dummy4):
	if win.fullscreen:
		win.set_fullscreen(fullscreen=False)
	else:
		win.set_fullscreen(fullscreen=True)
	resize()
		
def zoomm(x,y,dummy1,dummy2):
	global zoom,decx,decy
	if zoom>2:
		decx=decx+2*x
		decy=decy+2*y
		zoom=zoom-2
	
def zoomp(x,y,dummy1,dummy2):
	global zoom,decx,decy
	decx=decx-2*x
	decy=decy-2*y
	zoom=zoom+2
	
''' *********************************************************************************************** '''
''' Fonctions gestion du monde																		'''

def reallystop():
	global play,world,level,stat,stat_var,current,cycle,temp,nrj,rayon
	dat['run']['value']='stop'
	play=0
	clock.unschedule(calculate)
	current=worlds[world][level]['current']
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
				
def reallyrun():
		global play
		play=0.15625
		dat['run']['value']='run'
		clock.schedule_interval(calculate,play)
																			 
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
	clock.schedule_once(menu,2,level)
			
def itsvictory_ok():
	global world,level,finished
	reallystop()
	finished.extend(worlds[world][level]['link'])
	finished=list(set(finished))
	savelevel(world,level)
	sync()
	clock.schedule_once(menu,2,-1)
	
def gameover(x):
	global over
	over=x
	sound.queue(pyglet.resource.media("sound/gameover.mp3"))
	sound.play()
	clock.unschedule(calculate)

def itsvictory():
	global over
	over=-1
	sound.queue(pyglet.resource.media("sound/victoire.mp3"))
	sound.play()
	clock.unschedule(calculate)

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
	else:
		return positive(x)
	
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
clock.schedule(refresh)
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
pic_levels2=image.load("picture/levels2.png")
pic_locked=image.load("picture/locked.png")
document=pyglet.text.decode_attributed("test")
txt_description=pyglet.text.layout.TextLayout(document,dpi=72,multiline=True,width=732,height=140)
txt_description.x=8
txt_description.y=8
txt_cout2=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=780,y=120,bold=False,italic=False,color=(180, 180, 180,255))
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
txt_world=pyglet.text.Label("World",font_name='OpenDyslexicAlta',font_size=30,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_temp=pyglet.text.Label("",font_name='Mechanihan',font_size=20,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_son=pyglet.text.Label("Reglages du son",font_name='Mechanihan',font_size=30,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))
txt_video=pyglet.text.Label("Options Video",font_name='Mechanihan',font_size=30,x=0,y=0,bold=False,italic=False,color=(180, 180, 180,255))


''' *********************************************************************************************** '''
''' Fonctions evenementielles liees a la fenetre																	 '''
				
@win.event
def on_key_press(symbol, modifiers):
	global play,over,level
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
		run(0,0,0,0)
	elif symbol==key.NUM_SUBTRACT:
		speed(1980,2,0,0)
	elif symbol==key.NUM_ADD:
		speed(1980,1,0,0)

@win.event	
def on_mouse_motion(x, y, dx, dy):
	global world,selected,allcout,over,level,worlds,finished
	if level>=0: 
		realx=(x-decx)/zoom
		realy=(y-decy)/zoom
		if unroll==1:
			if debug==1:
				nbelements=44
			else:
				nbelements=29
			size=win.width/nbelements	
			allcout[2]=0
			allcout[0]=x
			allcout[1]=y
			for i in range(nbelements):
				if x>=5+i*size and x<=5+i*size+size and y>=55 and y<55+size:
					if art[int("0x30000",16)+i]['tech']<=tech:
						allcout[2]=art[int("0x30000",16)+i]
		return	
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
				
@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global zoom,mousel,mouser,mousem,over,level,unroll
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
	realx=(x-decx)/zoom
	realy=(y-decy)/zoom
	mouses=23
	if buttons == mouse.LEFT:
		mouses=mousel
	if buttons == mouse.RIGHT:
		mouses=mouser	
	if buttons == mouse.MIDDLE:
		mouses=mousem
	if mouses!=23 and dat[int("0x20000",16)+mouses]['drag']==1 and (unroll==0 or y>100) and (y>50):
		eval(dat[int("0x20000",16)+mouses]['nom']+"("+str(realx)+","+str(realy)+","+str(dx)+","+str(dy)+")")
			
@win.event
def on_mouse_press(x, y, button, modifiers):
	global zoom,mousel,mouser,mousem,unroll,over,level,selected,world
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
			readlevel(selected['world'],selected['level'],True)
			if selected['video']:
				player.queue(pyglet.resource.media('movie/level'+str(world)+"-"+str(level)+".mp4"))
				player.play()
				ambiance.pause()
				selected=-1
		return
	realx=(x-decx)/zoom
	realy=(y-decy)/zoom
	for i in range(15):
		if x>=10+i*45 and x<=49+i*45 and y>=8 and y<44:
			if 'color' in dat[int("0x20000",16)+i] and dat[int("0x20000",16)+i]['color']!=[40,40,40]:
				if button == mouse.LEFT:
					mousel=i
				if button == mouse.RIGHT:
					mouser=i	
				if button == mouse.MIDDLE:
					mousem=i
				if button!="" and i==14:
					if unroll==1:
						unroll=0
					else:
						unroll=1	
				if i>=11: return
	if unroll==1:
		if debug==1:
			nbelements=44
		else:
			nbelements=29
		size=win.width/nbelements	
		for i in range(nbelements):
			if x>=5+i*size and x<=5+i*size+size and y>=55 and y<55+size:
				if art[int("0x30000",16)+i]['tech']<=tech:
					dat['others']['ref']=art[int("0x30000",16)+i]
					if button == mouse.LEFT:
						mousel=14
					if button == mouse.RIGHT:
						mouser=14
					if button == mouse.MIDDLE:
						mousem=14
					return	
	mouses=23
	if button == mouse.LEFT:
		mouses=mousel
	if button == mouse.RIGHT:
		mouses=mouser	
	if button == mouse.MIDDLE:
		mouses=mousem
	if mouses!=23:
		eval(dat[int("0x20000",16)+mouses]['nom']+"("+str(realx)+","+str(realy)+","+str(0)+","+str(0)+")")
		
@win.event
def on_resize(width,height):
	resize()

if __name__ == '__main__':
    main()
