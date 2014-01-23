#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import pyglet
import copy
import csv
import random
import time
import operator
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from pyglet import clock
from pyglet import image


''' ************************************************************************************************ '''
''' Initialisation																											 '''

def loaditems(n,file):
	global items
	with open(file, 'rb') as f:
		liste=list(csv.reader(f,delimiter=';'))
		for i in range(1,len(liste)):
			items[liste[i][0]]={}
			for j in range(1,len(liste[i])):
				if liste[i][j][:1]=="#":
					items[liste[i][0]][liste[0][j]]=int(liste[i][j][1:])
				elif liste[i][j][:1]=="[":
					atemp=liste[i][j][1:-1].split(",")
					items[liste[i][0]][liste[0][j]]=[int(atemp[k]) for k in range(len(atemp))]
				elif liste[i][j][:1]=="{":
					atemp=items[liste[i][0]][liste[0][j]]=liste[i][j][1:-1].split(",")
					items[liste[i][0]][liste[0][j]]=[atemp[k] for k in range(len(atemp))]
				elif liste[i][j][:2]=="0x":
					items[liste[i][0]][liste[0][j]]=int(liste[i][j][2:],16)
				elif liste[i][j][:1]=="&":
					items[liste[i][0]][liste[0][j]]=float(liste[i][j][1:])
				elif liste[i][j][:1]=="@":
					items[liste[i][0]][liste[0][j]]=items[liste[i][j][1:]]			
				else:
					items[liste[i][0]][liste[0][j]]=liste[i][j]
			if n!=0:
				items[liste[i][0]]['value']=n+i-1
			items[items[liste[i][0]]['value']]=liste[i][0]
		f.close()
		return len(liste)-1
		
def initgrid(x,y):
	global adirection,sizeworld,finished,allcout,selected,world,level,over,mousel,mouser,mousem,sizex,sizey,world_old,world_new,world_art,items,direction,zoom,play,stat,cycle,cout,thecout,rayon,unroll,debug,temp,decx,decy,nrj,tech,victory,current,names,thecolors,maxnrj,maxrayon,maxcycle,maxtemp,nom,descriptif,element
	
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
	items = {}
	sizeworld=loaditems(int("0x40000", 16),"data/worlds.dat")	
	loaditems(int("0x30000", 16),"data/elements2.dat")	
	loaditems(int("0x10000", 16),"data/menus2.dat")	
	loaditems(int("0x20000", 16),"data/menus.dat")
	loaditems(0,"data/elements.dat")
		
	''' Variables globales '''
	sizex=x
	sizey=y
	zoom=25
	stat=[0,0,0,0,0,0,0,0]
	nom=descriptif=element='H'
	names=["e","e","q","e","e","e","e","K","L","M","N","n","p"]
	thecolors=[items['headb2']['color'],items['headb']['color'],items['headp']['color'],items['head']['color'],items['head2']['color'],items['headr']['color'],items['headr2']['color'],items['headb']['color'],items['headb']['color'],items['headb']['color'],items['headb']['color'],items['neut']['color'],items['prot']['color']]
	victory=[0,0,0,0,0,0,0,1,0,0,0,1,1]
	current=[0,0,0,0,0,0,0,0,0,0,0,0,0]
	finished=[]
	mousel=4
	mouser=0
	mousem=3
	maxnrj=maxrayon=maxcycle=maxtemp=99999
	allcout=thecout=world=over=play=cycle=rayon=temp=cout=decx=decy=unroll=nrj=debug=0
	selected=level=-1
	tech=9
	world_art = [[items['nothing']['value'] for y in range(sizey)] for x in range(sizex)]
	world_new = [[items['nothing']['value'] for y in range(sizey)] for x in range(sizex)]


''' *********************************************************************************************** '''
''' Sauvegarde/Restauration																								 '''

'''format nom,element,descriptif,debug,zoom,decx,decy,tech,victory     '''

def readpref(file):
	global finished
	with open(file, 'a+') as f:
		try:
			finished=list(csv.reader(f,delimiter=';'))[0]
			f.close()
		except:
			print "no"
							
def writepref(file):
	global finished
	with open(file, 'wb+') as f:
		writer = csv.writer(f, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE)
		writer.writerow(finished)
		f.close()		
		
def readlittlegrid(file,key):
	with open(file, 'rb') as f:
		liste=list(csv.reader(f,delimiter=';'))
		items[key]['nom']=liste[0][0]
		items[key]['element']=liste[0][1]
		items[key]['description']=liste[0][2]
		items[key]['tech']=int(liste[0][7])
		items[key]['cout']=int(liste[0][8])
		victemp=liste[0][9][1:len(liste[0][9])-1].split(",")
		items[key]['victory']=[int(victemp[k]) for k in range(len(victemp))]
		items[key]['maxcycle']=int(liste[0][15])
		items[key]['maxnrj']=int(liste[0][16])
		items[key]['maxrayon']=int(liste[0][17])
		items[key]['maxtemp']=int(liste[0][18])
		f.close()
		
def readcondgrid(file):
	global current,cycle,nrj,rayon,temp
	with open(file, 'rb') as f:
		liste=list(csv.reader(f,delimiter=';'))
		curtemp=liste[0][10][1:len(liste[0][10])-1].split(",")
		current=[int(curtemp[k]) for k in range(len(curtemp))]
		cycle=int(liste[0][11])
		nrj=int(liste[0][12])
		rayon=int(liste[0][13])
		temp=int(liste[0][14])
		f.close()

def readgrid(file):
	global unroll,mousel,mousem,mouser,cout,selected,sizex,sizey,world_old,world_new,world_art,items,zoom,play,stat,cycle,nrj,rayon,tech,decx,decy,unroll,stat,victory,current,temp,debug,nom,descriptif,element,maxnrj,maxrayon,maxcycle,maxtemp
	try:
		with open(file, 'rb') as f:
			liste=list(csv.reader(f,delimiter=';'))
			sizey=(len(liste)-1)/2
			sizex=len(liste[1])
			nom=liste[0][0]
			element=liste[0][1]
			descriptif=liste[0][2]
			debug=int(liste[0][3])
			zoom=int(liste[0][4])
			decx=int(liste[0][5])
			decy=int(liste[0][6])
			tech=int(liste[0][7])
			cout=int(liste[0][8])		
			victemp=liste[0][9][1:len(liste[0][9])-1].split(",")
			victory=[int(victemp[k]) for k in range(len(victemp))]
			curtemp=liste[0][10][1:len(liste[0][10])-1].split(",")
			current=[int(curtemp[k]) for k in range(len(curtemp))]
			cycle=int(liste[0][11])
			nrj=int(liste[0][12])
			rayon=int(liste[0][13])
			temp=int(liste[0][14])
			maxcycle=int(liste[0][15])
			maxnrj=int(liste[0][16])
			maxrayon=int(liste[0][17])
			maxtemp=int(liste[0][18])
			world_new = [[int(liste[sizey-i][j]) for i in range(sizey)] for j in range(sizex)]
			world_art = [[int(liste[-i-1][j]) for i in range(sizey)] for j in range(sizex)]		
			stat=[0,0,0,0,0,0,0,0]
			unroll=over=0
			if tech<0:
				items[items['setcopper']['value']]='setnothinga'
				items[items['setfiber']['value']]='setnothinga'
				items[items['setnothing']['value']]='setnothinga'
				items[items['others']['value']]='setnothinga'
			elif tech<2:
				items[items['setcopper']['value']]='setcopper'
				items[items['setfiber']['value']]='setnothinga'
				items[items['setnothing']['value']]='setnothing'
				items[items['others']['value']]='others'
			else:
				items[items['setcopper']['value']]='setcopper'
				items[items['setfiber']['value']]='setfiber'
				items[items['setnothing']['value']]='setnothing'
				items[items['others']['value']]='others'
			f.close()
			infos()
			return True
	except IOError:
		return False

def writegrid(file):
	global sizex,sizey,world_old,world_new,world_art,items,play,cycle,nom,element,descriptif,debug,zoom,decx,decy,tech,victory
	with open(file, 'wb') as f:
		writer = csv.writer(f, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE)
		writer.writerow([nom,element,descriptif,debug,zoom,decx,decy,tech,cout,str(victory),str(current),cycle,nrj,rayon,temp,maxcycle,maxnrj,maxrayon,maxtemp])
		for j in range(sizey):
			 writer.writerow([world_new[i][sizey-j-1] for i in range(sizex)])
		for j in range(sizey):
			 writer.writerow([wart(i,-j-1) for i in range(sizex)])
		f.close()
	
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
		player.get_texture().blit(0,0)
		return
	if level!=-1:
		drawgrid(zoom)
	else:
		drawworld()
	
''' *********************************************************************************************** '''
''' Affichage																													 '''	

def drawsquare(x,y,x2,y2,full,color):
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
	
def drawsemisquare(x,y,x2,y2,color):
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
	
def drawitdem(x,y,art,thezoom,activation):	
	if 'text' in art:
		if art['activable']==0:
			drawsquare(x+1,y+1,x+thezoom-1,y+thezoom-1,0,[255,255,255])
			label=pyglet.text.Label(art['text'].decode('utf-8'),font_name='Liberation Mono',font_size=thezoom,x=x+thezoom/10,y=y+thezoom/10,color=(art['color'][0],art['color'][1],art['color'][2],255))
		else:
			drawsemisquare(x+1,y+1,x+thezoom-1,y+thezoom-1,[255,255,255])
			if activation!=0:
				label=pyglet.text.Label(art['text'].decode('utf-8'),font_name='Liberation Mono',font_size=thezoom,x=x+thezoom/10,y=y+thezoom/10,color=(art['color'][0],art['color'][1],art['color'][2],55+200*activation/10))
			else:
				label=pyglet.text.Label(art['text'].decode('utf-8'),font_name='Liberation Mono',font_size=thezoom,x=x+thezoom/10,y=y+thezoom/10,color=(255,255,255,255))
		label.draw()
			
def drawstat(x,y,x2,y2,color):
	global thecolors,stat
	drawsquare(x,y,x2,y2,0,color)
	oldx=x
	for i in range(7):
		if stat[7]>0:
			newx=oldx+float(stat[i])*(x2-x)/stat[7]
		else:
			newx=oldx
		drawsquare(int(oldx),y,int(newx),y2,1,thecolors[i])
		oldx=newx
	label=pyglet.text.Label(str(stat[7]),font_size=24,x=x+(x2-x)/2-(len(str(stat[7])))*12,y=y-(y-24)/2,bold=False,italic=False,color=(255, 255, 255,255))
	label.draw()
	
def drawvictory(x,y,x2,y2,color):
	global thecolors,victory,current,names
	'''size=(x2-x)/sum(victory[i] for i in range(len(victory)))'''
	size=21
	for i in range(len(victory)):
		if victory[i]>0: 
			drawsquare(x+size*i,y,x+size*(i+1),y2,1,thecolors[i])
			drawsquare(x+size*i,y,x+size*(i+1),y2,0,[90,90,90])
			drawsquare(x+size*i,y,x+size*(i+1),int(y+float(current[i])/victory[i]*(y2-y)),1,[0,0,0])
			if victory[i]-current[i]>=0:
				label=pyglet.text.Label(str(victory[i]-current[i]),font_size=24,x=x+size*i,y=y,bold=False,italic=False,color=(255, 255, 255,255))
				label.draw()
			label=pyglet.text.Label(names[i],font_size=10,x=x+size*i,y=y2-10,bold=False,italic=False,color=(255, 255, 255,255))
			label.draw()
			
def drawtxt(x):
	text="{font_name 'Liberation Mono'}{font_size 22}{color (255, 255, 255, 255)}"+x+"}".encode('utf8')
	label=pyglet.text.layout.TextLayout(pyglet.text.decode_attributed(text),dpi=72,multiline=True,width=732,height=140)
	label.x=8
	label.y=8	
	label.draw()	
			
def drawworld():
	global selected,victory,finished
	glClear(GL_COLOR_BUFFER_BIT)
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	drawsquare(740,148,1016,8,1,[40,40,40])
	drawsquare(8,148,1016,8,0,[90,90,90])
	glColor3ub(255,255,255)
	pic=image.load("picture/logo.png")
	pic.blit(185,win.height-200)
	pic=image.load("picture/logo2.png")
	pic.blit(45,win.height-160)
	if selected==-2:
		glColor3ub(255,0,0)
	else:
		glColor3ub(255,255,255)
	pic=image.load("picture/exit2.png")
	pic.blit(940,win.height-100)
	if selected==-3:
		glColor3ub(255,0,0)
	else:
		glColor3ub(255,255,255)
	pic=image.load("picture/arrows.png")
	pic.blit(840,150)
	if selected==-4:
		glColor3ub(255,0,0)
	else:
		glColor3ub(255,255,255)
	pic=image.load("picture/arrows2.png")
	pic.blit(920,150)
	glColor3ub(255,255,255)	
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world:
			glBegin(GL_LINES)
			for n in ele['validate']:
				if items[n]['world']==world:
					glVertex2i(ele['coordx']+50,ele['coordy']+50)
					glVertex2i(items[n]['coordx']+50,items[n]['coordy']+50)
					glVertex2i(ele['coordx']+51,ele['coordy']+50)
					glVertex2i(items[n]['coordx']+51,items[n]['coordy']+50)
					glVertex2i(ele['coordx']+50,ele['coordy']+51)
					glVertex2i(items[n]['coordx']+50,items[n]['coordy']+51)
					glVertex2i(ele['coordx']+51,ele['coordy']+51)
					glVertex2i(items[n]['coordx']+51,items[n]['coordy']+51)
			glEnd()				
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world:
			if 'cout' not in ele:
				readlittlegrid(ele['file'],items[int("0x40000",16)+i])
			if items[int("0x40000",16)+i] not in finished and not (ele['world']==0 and ele['grid']==0):
				glColor3ub(60,60,60)
				acolor=(90,90,90,255)
			elif selected!=ele:
				glColor3ub(255,120+int(ele['coordx']/1024.0*135),155+int(ele['coordx']/1024.0*100))
				acolor=(90,90,90,255)
			else:
				acolor=(255,255,255,255)
				drawtxt(ele['description'].decode('utf-8'))
				glColor3ub(255,255,255)
				if ele['cout']>0:
					pic=image.load('picture/cout.png')
					pic.blit(740,110)
					label=pyglet.text.Label(str(ele['cout']),font_size=15,x=780,y=120,bold=True,italic=False,color=(110, 110, 110,255))
					label.draw()
				if ele['maxcycle']<90000:
					pic=image.load('picture/cycle.png')
					pic.blit(740,65)
					label=pyglet.text.Label(str(ele['maxcycle']),font_size=15,x=780,y=75,bold=True,italic=False,color=(110, 110, 110,255))
					label.draw()
				if ele['tech']>0:	
					pic=image.load('picture/tech.png')
					pic.blit(940,110)
					label=pyglet.text.Label(str(ele['tech']),font_size=15,x=980,y=120,bold=True,italic=False,color=(110, 110, 110,255))
					label.draw()
				if ele['maxrayon']<90000:	
					pic=image.load('picture/rayon.png')
					pic.blit(940,65)
					label=pyglet.text.Label(str(ele['maxrayon']),font_size=15,x=970,y=75,bold=True,italic=False,color=(110, 110, 110,255))
					label.draw()
				if ele['maxtemp']<90000:	
					pic=image.load('picture/temp.png')
					pic.blit(850,110)
					label=pyglet.text.Label(str(ele['maxtemp']),font_size=15,x=875,y=120,bold=True,italic=False,color=(110, 110, 110,255))
					label.draw()
				if ele['maxnrj']<90000:	
					pic=image.load('picture/nrj.png')
					pic.blit(850,65)
					label=pyglet.text.Label(str(ele['maxnrj']),font_size=15,x=875,y=75,bold=True,italic=False,color=(110, 110, 110,255))
					label.draw()
				victory=ele['victory']
				drawvictory(742,12,1016,50,[40,40,40])
				glColor3ub(255,0,0)
			pic=image.load("picture/levels2.png")
			pic.blit(ele['coordx'],ele['coordy'])
			label=pyglet.text.Label(ele['element'],font_name='Liberation Mono',font_size=15,x=ele['coordx']+50,y=ele['coordy']+70,bold=True,italic=False,color=(int(ele['coordx']/1024.0*150), int(ele['coordx']/1024.0*150), int(ele['coordx']/1024.0*150),255))
			label.draw()
			calc=(len(ele['nom'])*16-76)/2
			drawsquare(ele['coordx']+28-calc,ele['coordy']+2,ele['coordx']+28-calc+len(ele['nom'])*15,ele['coordy']-18,1,[40,int(ele['coordx']/1024.0*135),int(ele['coordx']/1024.0*100)])			
			label=pyglet.text.Label(ele['nom'].decode('utf-8'),font_name='Liberation Mono',font_size=16,x=ele['coordx']+38-calc,y=ele['coordy']-15,bold=True,italic=False,color=acolor)
			label.draw()
	
def drawgrid(zoom):
	global temp,debug,over,allcout,play
	glClear(GL_COLOR_BUFFER_BIT)
	drawsquare(decx-1+zoom,decy-1+zoom,decx+zoom*(sizex-1)+1,decy+zoom*(sizey-1)+2,0,[255,255,255])
	if play>0:
		drawsquare(decx-1+zoom,decy-1+zoom,decx+zoom*(sizex-1)+1,decy+zoom*(sizey-1)+2,0,[255,0,0])
		drawsquare(decx-2+zoom,decy-2+zoom,decx+zoom*(sizex-1)+2,decy+zoom*(sizey-1)+3,0,[255,0,0])			
	for x in range(1,sizex-1):
		if x*zoom+decx>win.width: break
		for y in range(1,sizey-1):
			if y*zoom+decy>win.height: break
			drawsquare(x*zoom+decx,y*zoom+decy,(x+1)*zoom+decx,(y+1)*zoom+decy,1,items[items[world_new[x][y]]]['color'])
			drawitdem(x*zoom+decx,y*zoom+decy,items[items[wart(x,y)]],zoom,getactive(x,y))
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
			art=items[items[int("0x30000",16)+i]]
			if art['tech']<=tech: 
				drawitdem(10+i*size,55,items[items[int("0x30000",16)+i]],size-6,10)
				if art['cat']!=cat:
					drawsquare(7+i*size,55,8+i*size,55+size,0,[90,90,90])
					cat=art['cat']
	drawsquare(615,win.height-45,655,win.height-5,1,[255,255,255])
	label=pyglet.text.Label(element,font_size=20,x=636-len(element)*10,y=win.height-35,bold=False,italic=False,color=(0, 0, 0,255))
	label.draw()
	if tech>3:	
		for i in range(4):
			glColor3ub(255,255,255)
			pic=image.load(items[items[int("0x10000",16)+i]]['icon'])
			pic.blit(10+i*150,win.height-45)
			label=pyglet.text.Label(str(eval(items[int("0x10000",16)+i])),font_size=24,x=50+i*150,y=win.height-29,bold=True,italic=False,color=(110, 110, 110,255))
			label.draw()
			label=pyglet.text.Label(str(eval("max"+items[int("0x10000",16)+i])),font_size=12,x=50+i*150,y=win.height-47,bold=True,italic=True,color=(110, 110, 110,255))
			label.draw()
	drawvictory(660,win.height-45,1020,win.height-5,[90,90,90])
	for i in range(15):
		glColor3ub(255,255,255)
		if items[items[int("0x20000",16)+i]]['icon']=="/":
			drawitdem(10+i*45,8,items[items[int("0x20000",16)+i]]['ref'],36,10)
		elif items[items[int("0x20000",16)+i]]['icon']!="":
			pic=image.load(items[items[int("0x20000",16)+i]]['icon'])
			pic.blit(10+i*45,8)
		else:
			drawsquare(10+i*45,8,46+i*45,44,1,items[items[int("0x20000",16)+i]]['color'])
		if i==11 or i==6:
			drawsquare(5+i*45,8,6+i*45,44,0,[90,90,90])
		if i==1:
			drawsquare(45+i*45,8,49+i*45,44,1,[0,0,0])
			drawsquare(45+i*45,8,49+i*45,44*10*len(str(play))/100,1,[255,0,0])	
		if (mousel==i):
			selectcolor=[255,0,0] 
		elif (mouser==i):
			selectcolor=[0,255,0]  
		elif (mousem==i):
			selectcolor=[0,0,255] 
		else:
			selectcolor=[40,40,40] 	
		drawsquare(10+i*45,8,46+i*45,44,0,selectcolor)
		drawsquare(9+i*45,7,47+i*45,45,0,selectcolor)
	drawsquare(5+15*45,8,6+15*45,44,0,[90,90,90])
	drawstat(10+15*45,8,46+(18)*45,44,[90,90,90])
	if tech>=0:	
		glColor3ub(255,255,255)
		pic=image.load(items[items[int("0x10000",16)+4]]['icon'])
		pic.blit(10+19*45,7)
		if (cout-thecout)>0:
			label=pyglet.text.Label(str(cout-thecout),font_size=15,x=46+19*45,y=18,bold=True,italic=False,color=(110, 110, 110,255))
		else:
			label=pyglet.text.Label(str(cout-thecout),font_size=15,x=46+19*45,y=18,bold=True,italic=False,color=(255, 0, 0,255))
		label.draw()
	if tech>0:
		glColor3ub(255,255,255)
		pic=image.load(items[items[int("0x10000",16)+5]]['icon'])
		pic.blit(25+21*45,7)
		label=pyglet.text.Label(str(tech),font_size=15,x=55+21*45,y=18,bold=True,italic=False,color=(110, 110, 110,255))
		label.draw()
	if over>0:
		label=pyglet.text.Label("GAME OVER",font_name='Liberation Mono',font_size=100,x=win.width/2-350,y=win.height/2-200,color=(255,255,255,255))
		label.draw()
		msg=["Trop de matière reçue dans les senseurs","Les photons sont sortis du cadre de jeu","Colision de protons et de neutrons","Le canon a provoqué une collision","Vous avez généré trop de rayonements","Le nombre de cycle maximum a été atteint","La température est a un niveau inacceptable","Il n'y a plus d'energie disponible !"]
		label=pyglet.text.Label(msg[over-1].decode('utf-8'),font_name='Liberation Mono',font_size=30,x=0,y=win.height/2-100,color=(255,255,255,255))
		label.draw()
	if over<0:
		label=pyglet.text.Label("VICTOIRE !",font_name='Liberation Mono',font_size=100,x=win.width/2-350,y=win.height/2-200,color=(255,255,255,255))
		label.draw()
		label=pyglet.text.Label("Vous débloquez le/les niveaux suivant.".decode('utf-8'),font_name='Liberation Mono',font_size=30,x=0,y=win.height/2-100,color=(255,255,255,255))
		label.draw()
	if allcout>0:
		label=pyglet.text.Label("cout:"+str(allcout['cout']),font_name='Liberation Mono',font_size=10,x=950,y=win.height-20,color=(255,255,255,255))
		label.draw()
		label=pyglet.text.Label("tech:"+str(allcout['tech']),font_name='Liberation Mono',font_size=10,x=950,y=win.height-40,color=(255,255,255,255))
		label.draw()
''' *********************************************************************************************** '''
''' Fonctions liees aux menus																								 '''
				
def raz(dummy1,dummy2,dummy3,dummy4):
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world and ele['grid']==level:
			readgrid(ele['file'])
	
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
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		value=items['others']['ref']['value']
		if value==items['null']['value']:
			value=items['nothing']['value']
		if world_new[x][y]!=items['fiber']['value'] and world_new[x][y]<items['tail']['value']: 
			if cout-thecout-items['others']['ref']['cout'] >= 0:
				world_art[x][y] = value
				infos()

def setnothinga(x,y,dummy1,dummy2):
	infos()
	
def setnothing(x,y,dummy1,dummy2):
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		if world_new[x][y]<items['tail']['value']: 
			world_new[x][y] = items['nothing']['value']
			world_art[x][y] = items['nothing']['value']
			infos()
		
def setcopper(x,y,dummy1,dummy2):
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		if world_new[x][y]<items['tail']['value']: 
			if cout-thecout-items['copper']['cout'] >= 0:
				world_new[x][y] = items['copper']['value']
				infos()
	
def setfiber(x,y,dummy1,dummy2):
	if x>=1 and y>=1 and x<sizex-1 and y<sizey-1 and play==0:
		if world_art[x][y]==0 and world_new[x][y]<items['tail']['value']: 
			if cout-thecout-items['fiber']['cout'] >= 0:
				world_new[x][y]=items['fiber']['value']
				infos()
		
def levels(dummy1,dummy2,dummy3,dummy4):
	global level,sizeworld
	reallystop()
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world and ele['grid']==level:
			writegrid("user/"+ele['file'])
	level=-1

def exits(dummy1,dummy2,dummy3,dummy4):
	pyglet.app.exit()
		
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
	global play,sizeworld,level
	items['run']['icon']="picture/stop.png"
	play=0
	clock.unschedule(calculate)
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world and ele['grid']==level:
			readcondgrid(ele['file'])
			erase()
			retriern()
				
def reallyrun():
		global play,sizeworld
		play=0.15625
		items['run']['icon']="picture/run.png"
		clock.schedule_interval(calculate,play)
																			 
def retriern():
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			art=wart(x,y)	
			typetri=items[art][:6]
			if typetri=="triern":
				acttri=""
				idtri=items[art][8]
				if len(items[art])==10: acttri=items[art][9]
				world_art[x][y]=items['triern'+idtri+"-"+idtri+acttri]['value']

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
	global over,level,sizeworld
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world and ele['grid']==level:
			readcondgrid(ele['file'])
			erase()
			writegrid("user/"+ele['file'])
	clock.schedule_once(menu,2,level)
			
def itsvictory_ok():
	global over,level,finished,sizeworld
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world and ele['grid']==level:
			readcondgrid(ele['file'])
			erase()
			writegrid("user/"+ele['file'])
			finished.extend(ele['validate'])
			writepref('user/pref.dat')
	clock.schedule_once(menu,2,-1)
	
def gameover(x):
	global over
	reallystop()
	over=x
	sound.queue(pyglet.resource.media("sound/gameover.mp3"))
	sound.play()

def itsvictory():
	global over
	reallystop()
	label=pyglet.text.Label("ViCTOIRE !",font_name='Liberation Mono',font_size=100,x=win.width/2-350,y=win.height/2-200,color=(255,255,255,255))
	over=-1
	sound.queue(pyglet.resource.media("sound/victoire.mp3"))
	sound.play()

def infos():
	global stat,sizex,sizey,cycle,thecout,victory,current
	stat=[0,0,0,0,0,0,0,0]
	thecout=0
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			if world_new[x][y]==items['headb2']['value']: stat[0]=stat[0]+1
			if world_new[x][y]==items['headb']['value']: stat[1]=stat[1]+1
			if world_new[x][y]==items['headp']['value']: stat[2]=stat[2]+1
			if world_new[x][y]==items['head']['value']: stat[3]=stat[3]+1
			if world_new[x][y]==items['head2']['value']: stat[4]=stat[4]+1
			if world_new[x][y]==items['headr']['value']: stat[5]=stat[5]+1
			if world_new[x][y]==items['headr2']['value']: stat[6]=stat[6]+1
			if world_new[x][y]>=items['head']['value']: stat[7]=stat[7]+1
			if cycle!=0: desactive(x,y)
			thecout=items[items[world_new[x][y]]]['cout']+items[items[wart(x,y)]]['cout']+thecout
		tempvictoire=0
	for i in range(len(victory)):
		if victory[i]-current[i]<0:
			gameover(1)
			break
		tempvictoire=(victory[i]-current[i])|tempvictoire
	if tempvictoire==0: itsvictory()	
	if rayon>maxrayon: gameover(5)
	if cycle>maxcycle: gameover(6)
	if temp>maxtemp: gameover(7)
	if nrj>maxnrj: gameover(8)
	
def erase():
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			if world_new[x][y]==items['headp']['value'] or world_new[x][y]==items['tailp']['value']:
				world_new[x][y]=items['fiber']['value']
			elif world_new[x][y]>=items['tail']['value']:
				world_new[x][y]=items['copper']['value']
			elif world_new[x][y]>=items['prot']['value']:
				world_new[x][y]=items['nothing']['value']
				
def wart(x,y):
	return world_art[x][y] & int("0xFFFFFF",16)
	
def getactive(x,y):
	return (world_art[x][y] & int("0xFF000000",16))>>24

def isactive(x,y):
	return world_art[x][y]>int("0xFFFFFF",16)
		
def desactive(x,y):
	if world_art[x][y]>int("0x1000000",16):
		world_art[x][y]=world_art[x][y]-int("0x1000000",16)
		
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
	return n[0]==1 and n[1]==0
	
def isdroite(n):
	return n[0]==-1 and n[1]==0

def nextgrid():
	global play,cycle,temp,rayon,nrj,current,adirection
	world_old=copy.deepcopy(world_new)
	swap()
	for x in range(1,sizex-1):
		for y in range(1,sizey-1):
			value=world_old[x][y]
			flag=0
			if (wart(x,y)==items['canonh']['value'] or wart(x,y)==items['canonh2']['value']) and ((cycle%40==0 and isactive(x,y)==False) or (cycle%10==0 and isactive(x,y))):
				if world_new[x][y]>=items['head']['value']:
					gameover(4)
				elif world_new[x][y]==items['nothing']['value']:
					temp=temp+5					
				else:
					world_new[x][y]=items['head']['value']
					nrj=nrj+1
			if wart(x,y)==items['canont']['value'] and ((cycle%40==0 and isactive(x,y)==False) or (cycle%10==0 and isactive(x,y))):
				world_new[x][y]=items['tail']['value']
			if world_old[x][y] == items['headp']['value']:
				world_new[x][y]=items['tailp']['value']
			elif world_old[x][y] >= items['head']['value']:
				for dx,dy in adirection:
						if world_old[x+dx][y+dy]>=value>>8:
							break
				for ex,ey in direction[(dx,dy)]:
						if world_new[x+ex][y+ey]==items['headr']['value'] and world_new[x][y]==items['headr']['value']:
							world_old[x+ex][y+ey]=items['headr2']['value']
							world_new[x+ex][y+ey]=items['headr2']['value']
							world_new[x][y]=items['copper']['value']
							break
						if world_new[x+ex][y+ey]==items['headb']['value'] and world_new[x][y]==items['headb']['value']:
							world_old[x+ex][y+ey]=items['headb2']['value']
							world_new[x+ex][y+ey]=items['headb2']['value']
							world_new[x][y]=items['copper']['value']
							break
						if (world_new[x+ex][y+ey]==items['headb']['value'] and world_new[x][y]==items['headr']['value']) or (world_new[x+ex][y+ey]==items['headr']['value'] and world_new[x][y]==items['headb']['value']): 
							world_old[x+ex][y+ey]=items['copper']['value']
							world_new[x+ex][y+ey]=items['copper']['value']	
							world_new[x][y]=items['copper']['value']
							break		
						if (world_new[x+ex][y+ey]==items['headb2']['value'] and world_new[x][y]==items['headr2']['value']) or (world_new[x+ex][y+ey]==items['headr2']['value'] and world_new[x][y]==items['headb2']['value']):
							world_old[x+ex][y+ey]=items['nothing']['value']
							world_new[x+ex][y+ey]=items['nothing']['value']
							world_new[x][y]=items['nothing']['value']
							rayon=rayon+5
							break
						if world_new[x+ex][y+ey]==items['headr2']['value'] and world_new[x][y]==items['headb']['value']: 
							world_old[x+ex][y+ey]=items['headr']['value']
							world_new[x+ex][y+ey]=items['headr']['value']
							world_new[x][y]=items['copper']['value']
							rayon=rayon+1
							break
						if world_new[x+ex][y+ey]==items['headb2']['value'] and world_new[x][y]==items['headr']['value']: 
							world_old[x+ex][y+ey]=items['copper']['value']
							world_new[x+ex][y+ey]=items['copper']['value']
							world_new[x][y]=items['headr']['value']
							rayon=rayon+1
							break
						art=wart(x+ex,y+ey)
						if flag==0 and world_old[x+ex][y+ey]==items['copper']['value'] and world_new[x+ex][y+ey]<items['head']['value'] and art!=items['triern0-1']['value']  and art!=items['triern0-2']['value']  and art!=items['triern0-4']['value'] and (art!=items['triern0-4a']['value'] or isactive(x+ex,y+ey)) and (art!=items['triern0-8a']['value'] or isactive(x+ex,y+ey)) and (art!=items['trierp']['value'] or isactive(x+ex,y+ey)) and (art!=items['dir2']['value'] or isdroite((dx,dy))) and (art!=items['dir1']['value'] or isgauche((dx,dy))) and (art!=items['trierg']['value'] or isbig(value)) and (art!=items['trierr']['value'] or ispositive(value)) and (art!=items['trierb']['value'] or isnegative(value)):			
							if art==items['destroyer']['value']:
								world_new[x+ex][y+ey]=items['copper']['value']
							elif art==items['positiver']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=positive(value)
								value=positive(value)
							elif art==items['positiver2']['value']:
								world_new[x+ex][y+ey]=positive(value)
								value=positive(value)
							elif art==items['negativer']['value'] and isactive(x+ex,y+ey):				
								world_new[x+ex][y+ey]=negative(value)
								value=negative(value)
							elif art==items['inverter']['value']:			
								world_new[x+ex][y+ey]=invert(value)
								value=invert(value)
							elif art==items['neutraliser']['value']:				
								world_new[x+ex][y+ey]=unsigned(value)
								value=unsigned(value)
							elif art==items['reactor']['value'] and value==items['headr2']['value'] and isactive(x+ex,y+ey):				
								world_new[x+ex][y+ey]=items['copper']['value']
								world_new[x+ex][y+ey-1]=items['prot']['value']
							elif art==items['reactor']['value'] and value==items['head2']['value'] and isactive(x+ex,y+ey):				
								world_new[x+ex][y+ey]=items['copper']['value']
								value=items['copper']['value']
								world_new[x+ex][y+ey-1]=items['neut']['value']
							elif art==items['senserK']['value'] and value==items['headr']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=items['copper']['value']
								current[7]=current[7]+1
							elif art==items['senserL']['value'] and value==items['headr']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=items['copper']['value']
								current[8]=current[8]+1
							elif art==items['senserM']['value'] and value==items['headr']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=items['copper']['value']
								current[9]=current[9]+1
							elif art==items['senserN']['value'] and value==items['headr']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=items['copper']['value']
								current[10]=current[10]+1
							elif art==items['sensere']['value'] and value==items['head']['value']:
								world_new[x+ex][y+ey]=items['copper']['value']
								current[3]=current[3]+1
							elif art==items['senserf']['value'] and value==items['headr']['value']:
								world_new[x+ex][y+ey]=items['copper']['value']
								current[5]=current[5]+1
							elif art==items['senserg']['value'] and value==items['headb2']['value']:
								world_new[x+ex][y+ey]=items['copper']['value']
								current[0]=current[0]+1
							elif art==items['senserh']['value'] and value==items['head']['value'] and isactive(x+ex,y+ey):
								world_new[x+ex][y+ey]=items['copper']['value']
								current[3]=current[3]+1
							elif art==items['calor']['value']:				
								temp=temp-11
								world_new[x+ex][y+ey]=items['copper']['value']
							elif art==items['photonizer']['value'] and value<items['head2']['value']:		
								world_new[x+ex][y+ey]=items['copper']['value']
								for fx,fy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)):
									if world_new[x+ex+fx][y+ey+fy]==items['fiber']['value']:
										world_new[x+ex+fx][y+ey+fy]=items['headp']['value']
										break
							elif art==items['photonizer2']['value'] and value<items['head2']['value']:		
								world_new[x+ex][y+ey]=value
								for fx,fy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)):
									if world_new[x+ex+fx][y+ey+fy]==items['fiber']['value']:
										world_new[x+ex+fx][y+ey+fy]=items['headp']['value']
							else:
								world_new[x+ex][y+ey]=value
							flag=1
							typetri=items[art][:6]
							if typetri=="triern":
								acttri=""
								numtri=int(items[art][6])
								idtri=items[art][8]
								if len(items[art])==10: acttri=items[art][9]
								if acttri=="a" and isactive(x+ex,y+ey):
									if numtri>0: numtri=numtri-1
								else:
									if numtri>0: numtri=numtri-1
								world_art[x+ex][y+ey]=items['triern'+str(numtri)+"-"+idtri+acttri]['value']
							if	art!=items['nothing']['value'] and world_new[x][y]>=items['head']['value']:
								temp=items[items[art]]['temp']+temp
							world_new[x][y] = value>>8
							break
			elif value == items['tailp']['value']:
				world_new[x][y]=items['fiber']['value']
			elif value >= items['tail']['value'] and world_new[x][y] < items['head']['value']:
				newvalue=value-int("0x10", 16)
				if newvalue<items['tail']['value']: newvalue=items['copper']['value']
				world_new[x][y] = newvalue
			elif value == items['fiber']['value']:
				n=sum(world_old[x+dx][y+dy]==items['headp']['value'] for dx,dy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)))
				if 1 <= n <= 2:
					world_new[x][y]=items['headp']['value']
					for dx,dy in ((-1,-1),(-1,+0),(-1,+1),(+0,-1),(+0,+1),(+1,-1),(+1,+0),(+1,+1)):
						if wart(x+dx,y+dy)!=0 and items[items[wart(x+dx,y+dy)]]['activable']==1: 
							active(x+dx,y+dy)
				else:
					items['fiber']['value']
			elif value == items['prot']['value'] or value == items['neut']['value'] :
				if wart(x,y)==items['sensern']['value'] and value==items['neut']['value'] and isactive(x,y):
					world_new[x][y]=items['copper']['value']
					current[11]=current[11]+1
				elif wart(x,y)==items['senserp']['value'] and value==items['prot']['value'] and isactive(x,y):
					world_new[x][y]=items['nothing']['value']
					current[12]=current[12]+1
				elif world_new[x][y-1] == items['nothing']['value']:
					if y==1:
						gameover(2)
						return
					else:
						world_new[x][y-1] = value
						world_new[x][y] = items['nothing']['value']
				elif world_new[x][y-1] == items['prot']['value'] or world_new[x][y-1] == items['neut']['value']:
					gameover(2)
					return
	infos()
	cycle=cycle+1
	
''' *********************************************************************************************** '''
''' Lancement & initialisation																							 '''
				
def main():
   pyglet.app.run()
   
win = pyglet.window.Window(width=1024, height=768,resizable=True, visible=True)

initgrid(30,20)
win.set_caption("Wirechem: The new chemistry game")
clock.schedule(refresh)
player = pyglet.media.Player()
ambiance = pyglet.media.Player()
sound = pyglet.media.Player()
ambiance.queue(pyglet.resource.media("music/ambiance1.mp3"))
ambiance.play()
readpref('user/pref.dat')
world=0
for i in range(sizeworld):
	if items[int("0x40000",16)+i] in finished and items[items[int("0x40000",16)+i]]['world']>world:
		world=items[items[int("0x40000",16)+i]]['world']

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
	global world,selected,allcout,over,level,sizeworld,finished
	if level>=0: 
		realx=(x-decx)/zoom
		realy=(y-decy)/zoom
		if unroll==1:
			if debug==1:
				nbelements=44
			else:
				nbelements=29
			size=win.width/nbelements	
			allcout=0
			for i in range(nbelements):
				if x>=5+i*size and x<=5+i*size+size and y>=55 and y<55+size:
					if items[items[int("0x30000",16)+i]]['tech']<=tech:
						allcout=items[items[int("0x30000",16)+i]]
		return	
	selected=-1
	for i in range(sizeworld):
		ele=items[items[int("0x40000",16)+i]]
		if ele['world']==world:
			if x>ele['coordx']+20 and x<ele['coordx']+100 and y>ele['coordy']+0 and y<ele['coordy']+110 and (items[ele['value']] in finished or items[ele['value']]=="level0-0"):
				selected=ele
	if x>940 and y>win.height-100 and x<1024 and y<win.height:
		selected=-2
	if x>840 and y>150 and x<920 and y<240:
		selected=-3
	if x>920 and y>150 and x<1024 and y<240:
		selected=-4	
				
@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global zoom,mousel,mouser,mousem,over,level
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
	if mouses!=23 and items[items[int("0x20000",16)+mouses]]['drag']==1 and (unroll==1 or y>100) and (unroll==0 or y>50):
		eval(items[int("0x20000",16)+mouses]+"("+str(realx)+","+str(realy)+","+str(dx)+","+str(dy)+")")
			
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
		elif selected==-4 and world>0:
			world=world-1
		elif selected==-3 and world<2:
			world=world+1
		elif selected>-1:
			level=selected['grid']
			if readgrid("user/"+selected['file'])==False : readgrid(selected['file'])
			if selected['tuto']!="":
				player.queue(pyglet.resource.media(selected['tuto']))
				player.play()
				ambiance.pause()
				selected=-1
			return
	realx=(x-decx)/zoom
	realy=(y-decy)/zoom
	for i in range(15):
		if x>=10+i*45 and x<=49+i*45 and y>=8 and y<44:
			if 'color' in items[items[int("0x20000",16)+i]] and items[items[int("0x20000",16)+i]]['color']!=[40,40,40]:
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
					return
	if unroll==1:
		if debug==1:
			nbelements=44
		else:
			nbelements=29
		size=win.width/nbelements	
		for i in range(nbelements):
			if x>=5+i*size and x<=5+i*size+size and y>=55 and y<55+size:
				if items[items[int("0x30000",16)+i]]['tech']<=tech:
					items['others']['ref']=items[items[int("0x30000",16)+i]]
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
		eval(items[int("0x20000",16)+mouses]+"("+str(realx)+","+str(realy)+","+str(0)+","+str(0)+")")

if __name__ == '__main__':
    main()
