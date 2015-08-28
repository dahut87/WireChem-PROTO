#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
  ------------------------------------------
  
  Microlinux
  
  Programme principal

  (C) Copyright 2013-2014 Nicolas Hordé
  
  ------------------------------------------
'''
import subprocess
import datetime
import math
import copy
import random
import time
import operator
import os
import sys
import socket
import httplib
import urllib

import pyglet
from GLclass import *
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from pyglet import clock
from pyglet import image
from git import Git

''' *********************************************************************************************** '''
''' initialisation																		'''

global debug,user,hostname
hostname=socket.getfqdn()
user=""
debug = 1
animate = 0

''' *********************************************************************************************** '''
''' Gestion du menu principal																						 '''

#Classe du menu principal
class menu(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        global debug, worlds, world
        super(menu, self).__init__(resizable=True, fullscreen=True, visible=True,
                                   caption="Microlinux - Lancement")

        self.set_mouse_cursor(cursors['cross'])
        self.batch = pyglet.graphics.Batch()
        self.p0 = pyglet.graphics.OrderedGroup(0)
        self.p1 = pyglet.graphics.OrderedGroup(1)
        self.p2 = pyglet.graphics.OrderedGroup(2)
        self.p3 = pyglet.graphics.OrderedGroup(3)
        self.p4 = pyglet.graphics.OrderedGroup(4)
        self.clocks = [clock.schedule(self.draw)]
        self.count=0
        self.focus = None
        self.icons = [ainter(self, 20, self.height-185, pyglet.resource.image('picture/restart.png'), 'Redemarre la machine instantanement.', 'Redemarrer', 'sudo reboot',font="Mechanihan")]
        self.icons.extend([ainter(self, 20+self.icons[0].width*1.4, self.height-185, pyglet.resource.image('picture/eteindre.png'), "Eteindre votre ordinateur.", 'Eteindre', 'sudo halt',font="Mechanihan"),
                      ainter(self, 20+2*self.icons[0].width*1.4, self.height-185, pyglet.resource.image('picture/terminal.png'), "Lancement d'un terminal.", 'Terminal', 'xterm',font="Mechanihan"),
                      ainter(self, self.width-20-self.icons[0].width*1.4, 60+self.icons[0].width*0.6, pyglet.resource.image('picture/web.png'), 'Site internet de WireChem...', 'Site WWW', 'netsurf http://evolving.fr',font="Mechanihan"),
                      ainter(self, self.width-20-2*self.icons[0].width*1.4, 60+self.icons[0].width*0.6, pyglet.resource.image('picture/bug.png'), 'Soumettre un bogue ou un rapport de bêta testeur.', 'Beta-test', 'netsurf http://evolving.fr/ecrire/special.php?login=pinon&pass=poppop&where=14',font="Mechanihan"),
                      ainter(self, self.width-20-3*self.icons[0].width*1.4, 60+self.icons[0].width*0.6, pyglet.resource.image('picture/compte.png'), 'Votre compte...', 'Mon compte', 'netsurf http://evolving.fr',font="Mechanihan"),
                      ainter(self, 20, 60+self.icons[0].width*0.6, pyglet.resource.image('picture/wirechem.png'), "Lancer le jeu WireChem", 'WireChem', '/srv/launch',font="Mechanihan"),
                      ainter(self, self.width-400-self.icons[0].width*1.4, self.height-185, pyglet.resource.image('picture/musique.png'), "Réglage du son.", 'Son...', 'gnome-alsamixer',font="Mechanihan"),
                      ainter(self, self.width-400-2*self.icons[0].width*1.4, self.height-185, pyglet.resource.image('picture/net.png'), "Réglage du Réseau.", 'Reseau...', '/srv/network',font="Mechanihan"),
                      ainter(self, self.width-400-3*self.icons[0].width*1.4, self.height-185, pyglet.resource.image('picture/ecran.png'), "Configuration des options vidéo.", 'Video...', 'arandr',font="Mechanihan"),
                      ainter(self, 20, self.height/2-40, pyglet.resource.image('picture/info.png'), "Information sur la version du logiciel WireChem.", 'Informations', 'netsurf file:///srv/infos.html',font="Mechanihan")])
        self.rects=[arect(self,10, 10, self.width-20,125, typeof="both", color=(100,100,100,200), group=self.p3)]
        self.hostname=alabel(self,10,self.height-15,text=hostname,font='Deja vu',size=12,group=self.p4)
        self.dialog=[alabel(self,self.width-380,self.height-60,text='identifiant :',font='Deja vu',size=16,group=self.p4,visible=False),
                     alabel(self,self.width-380,self.height-120,text='mot de passe :',font='Deja vu',size=16,group=self.p4,visible=False),
                     atext(self,self.width-215,self.height-65,170,0,text="",font='Deja vu',align="left",size=16,visible=False),
                     atext(self,self.width-215,self.height-125,170,0,text="",font='password',align="left",size=16,visible=False),
                     abutton(self,self.width-190, self.height-195,0,0,"connect",content=pyglet.resource.image('picture/connexion.png'),typeof="icon",visible=False),
                     arect(self,self.width-400,self.height-230,390,220,typeof="face", color=(100,100,100,200), group=self.p3,visible=False),
                     arect(self,self.width-218,self.height-65,175,25,typeof="face", color=(150,150,150,255), group=self.p2,visible=False),
                     arect(self,self.width-218,self.height-125,175,25,typeof="face", color=(150,150,150,255), group=self.p2,visible=False)]
        self.dialog[4].sprite.group=self.p4
        self.dialog2=[alabel(self,0,0,text='',font='Deja vu',size=16,group=self.p4,visible=False),
                     abutton(self, 0, 0,0,0,"deconnect",content=pyglet.resource.image('picture/deconnexion.png'),typeof="icon",visible=False),
                     arect(self,0,0,290,90,typeof="face", color=(100,100,100,200), group=self.p2,visible=False)]
        self.dialog2[1].sprite.group=self.p4
        self.infos=[atext(self, 10, 10, self.width-10, 125, font="Mechanihan", size=18, align="left")]
        self.fond = abutton(self, "(self.window.width-800)/2", "(self.window.height-175+125)/2", 0, 0,"fond",content=pyglet.resource.image('picture/logo3.png'),typeof='icon')
        self.fond.sprite.group=self.p0
        self.setfocus(self.dialog[2])
        self.icons[4].visible=False
        self.icons[5].visible=False
        self.icons[4].update(0)
        self.icons[5].update(0)                     
        self.update(0)

        
        self.geticons()
        
    def geticons(self):
		global user
		ui = Git(".")
		try:
			version_temp=ui.ls_remote("git://github.com/dahut87/WireChem.git")
			version=version_temp.replace('\n','\t').split('\t')
			add=0
			for i in range(len(version)):
				if i%2==1 and version[i]!="HEAD" and '^' not in version[i]:
					add+=1
					self.icons.append(ainter(self, 20+add*(self.icons[0].width*1.4), 60+self.icons[0].width*0.6, pyglet.resource.image('picture/git.png'), "Lancer le jeu WireChem dans une version particulière de développement.", os.path.basename(version[i]), 'xterm -e /srv/launch '+os.path.basename(version[i]),font="Mechanihan"))
				self.icons.append(ainter(self, self.width-20-self.icons[0].width*1.4, self.height/2-40, pyglet.resource.image('picture/connect.png'), "Le système est connecté au réseau et opérationnel, double cliquez pour rafraichir !", "Connecte", 'killall python',font="Mechanihan"))
		except:
			self.icons.append(ainter(self, self.width-20-self.icons[0].width*1.4, self.height/2-40, pyglet.resource.image('picture/disconnect.png'), "Le système n'est pas convenablement connecté au réseau, double cliquez pour réessayer !", "Deconnecte", 'killall python',font="Mechanihan"))

    def update(self, what):
        global user
        if user!="":
            self.hidemdp()
            self.showlog()
        else:
            self.hidelog()
            self.showmdp()
            
    def connectsite(self, user, password):
		print user,password
		params = urllib.urlencode({'login': user, 'pass': password})
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		conn = httplib.HTTPConnection("wirechem.dahut.fr:80")
		conn.request("POST", "/ecrire/special.php", params, headers)
		response = conn.getresponse()
		state=''
		if response.status==200:
			state = response.read()
		conn.close()
		if state=="1":
			return True
		else:
			return False

    def draw(self, dt):
        glClear(GL_COLOR_BUFFER_BIT)
        self.batch.draw()

    def hidemdp(self):
        for i in range(len(self.dialog)):
            self.dialog[i].visible=False
            self.dialog[i].update(0)

    def showmdp(self):
        for i in range(len(self.dialog)):
            self.dialog[i].visible=True
            self.dialog[i].update(0)
        self.setfocus(self.dialog[2])

    def showlog(self):
        global user
        self.dialog2[0].visible=True
        self.dialog2[0].text=user
        self.dialog2[0].x=self.width+(self.dialog2[0].content_width-300)/2-self.dialog2[0].content_width
        self.dialog2[0].y=self.height-35
        self.dialog2[1].visible=True
        self.dialog2[1].x=self.width-self.dialog2[1].width-62
        self.dialog2[1].y=self.height-85
        self.dialog2[1].update(0)
        self.dialog2[2].visible=True
        self.dialog2[2].x=self.width-300
        self.dialog2[2].y=self.height-100
        self.dialog2[2].update(0)

    def hidelog(self):
        for i in range(len(self.dialog2)):
            self.dialog2[i].visible=False
            self.dialog2[i].update(0)

    def anime(self,dt):
        global animate
        if animate==0:
            self.infos[0].text="Mot de passe incorrect !! Veuillez retaper votre mot de passe s'il vous plait."
            self.infos[0].update(0)
            animate=16*math.pi
        animate-=math.pi/4
        if animate>0:
            clock.schedule_once(self.anime,0.02)
        else:
            animate=0
            self.infos[0].text=" "
            self.infos[0].update(0)
        for i in range(len(self.dialog)):
            self.dialog[i].x+=int(5*math.sin(animate))
            if hasattr(self.dialog[i],"update"):
                self.dialog[i].update(0)

### Evenements ###

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in [self.dialog[2],self.dialog[3]]:
            if widget.hit_test(x, y):
                self.setfocus(widget)
                break
        else:
            self.setfocus(None)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        for widget in [self.dialog[2],self.dialog[3]]:
            if widget.hit_test(x, y):
                self.set_mouse_cursor(cursors["text"])
                break
            else:
                self.set_mouse_cursor(cursors["cross"])

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        global user
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1
            all=(self.dialog[2],self.dialog[3])
            if self.focus in all:
                i = all.index(self.focus)
            else:
                i = 0
                dir = 0
            self.setfocus(all[(i + dir) % len(all)])
        elif symbol == key.ESCAPE:
            if debug==0:
                return pyglet.event.EVENT_HANDLED
            else:
                pyglet.app.exit()
        elif symbol == key.F5:
            self.close()
            launch()
        elif symbol == key.ENTER:
            if user=="":
                self.on_mouse_press_connect([])

    def setfocus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0
        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)

### Evenement générer par classe abutton ###

    def on_mouse_press_deconnect(self, state):
		global user
		user=""
		self.icons[len(self.icons)-1].content=pyglet.resource.image('picture/connect2.png')
		self.icons[len(self.icons)-1].update(0)
		self.update(0)

    def on_mouse_press_connect(self, state):
        global user
        if animate>0:
            return
        if self.connectsite(self.dialog[2].layout.document.text,self.dialog[3].layout.document.text):
			user=self.dialog[2].layout.document.text
			self.icons[len(self.icons)-1].content=pyglet.resource.image('picture/connect2.png')
			self.icons[len(self.icons)-1].update(0)
			self.update(0)
        else:
			user=''
			self.anime(0.02)

    def on_mouse_enter_item(self, n, state):
            self.infos[0].text=self.icons[n].hint
            self.infos[0].update(0)
            self.set_mouse_cursor(cursors['pointer'])
            self.icons[n].setselected([255, 120, 120])

    def on_mouse_leave_item(self, n, state):
            self.infos[0].text=" "
            self.infos[0].update(0)
            self.set_mouse_cursor(cursors['cross'])
            self.icons[n].setselected(False)

    def on_mouse_release_item(self, n, state):
            self.set_mouse_cursor(cursors['cross'])

    def on_mouse_double_item(self, n, state):
        process = subprocess.Popen(self.icons[n].cmd.split(" "))
        self.close()
        process.wait()
        launch()

    def on_mouse_drag_item(self, n, state):
        self.set_mouse_cursor(cursors['move'])
        self.icons[n].x += state['dx']
        self.icons[n].y += state['dy']
        if state['dx']<0 and self.icons[n].x<20 : self.icons[n].x=0
        if state['dx']>0 and self.icons[n].x>self.width-self.icons[n].width-20 : self.icons[n].x=self.width-self.icons[n].width
        if state['dy']<0 and self.icons[n].y<20-self.icons[n].height : self.icons[n].y=0
        if state['dy']>0 and self.icons[n].y>self.height-self.icons[n].height-20 : self.icons[n].y=self.height-self.icons[n].height
        print str(self.icons[n].y)+","+str(self.icons[n].x)
        self.icons[n].update(0)

def launch():
    menu_principal = menu()
    menu_principal.set_minimum_size(1024, 768)
    glEnable(GL_BLEND)
    #glEnable(GL_LINE_SMOOTH)
    #glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    pyglet.app.run()

''' *********************************************************************************************** '''
''' Lancement du menu principal
													'''
pyglet.resource.add_font('font/Mecanihan.ttf')
pyglet.resource.add_font('font/password.ttf')
cursors = {'pointer':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/pointer.png'), 15, 46),
           'text':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/text.png'), 24, 30),
           'move':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/move.png'), 24, 24),
           'create':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/create.png'), 12, 17),
           'cross':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/cross.png'), 24, 33),
           'delete':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/delete.png'), 24, 32)}
launch()
