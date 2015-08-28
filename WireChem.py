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
import copy
import csv
import random
import time
import operator
import shelve
import os
import sys
from os.path import expanduser

import pyglet
from GLclass import *
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from pyglet import clock
from pyglet import image


''' *********************************************************************************************** '''
''' Fonctions de chargement

																							'''
class io(object):

# Enregistre les données utilisateurs
    def sync(self):
        global Uworlds, finished
        self.write(self.gethome() + "/dbdata", ["Uworlds", "finished"])

# Enregistre les données système
    def rebase(self):
        global worlds
        self.write("dbdata", ["worlds"])


#Vérifie l'existence de la base de donnée utilisateur
    def verifyhome(self):
        global Uworlds, finished
        if not os.path.exists(self.gethome()):
            os.makedirs(self.gethome())
        if not os.path.exists(self.gethome() + "/dbdata"):
            Uworlds = [[{0: 0}]]
            finished = [(0, 0)]
            self.sync()


#Trouve le chemin vers le repertoire utilisateur
    def gethome(self):
        home = expanduser("~") + "/.wirechem"
        return home


#Ecrit les variables spécifiés dans la base selectionnée (utilisateur ou système)
    def write(self, afile, var):
        d = shelve.open(afile, writeback=True)
        for k in var:
            d[k] = copy.deepcopy(globals()[k])
        d.sync()
        d.close()


#Lit une base de donnée
    def read(self, afile):
        d = shelve.open(afile, writeback=True)
        for k in d.keys():
            globals()[k] = copy.deepcopy(d[k])
        d.close()


#Charge le dictionnaire sous forme de variables
    def load(d):
        for k in d.keys():
            if k[0] != "_":
                globals()[k] = copy.deepcopy(d[k])


#Référence les variables
    def reference(self, var, noms):
        if len(noms) == 2:
            for y in range(len(var)):
                for x in range(len(var[y])):
                    var[y][x][noms[0]] = y
                    var[y][x][noms[1]] = x
        else:
            for x in range(len(var[y])):
                var[x][y][noms[0]] = x


#duplique les références
    def duplicateref(self, d):
        for k in d.keys():
            d[d[k]['nom']] = d[k]

    def readlevel(self, w, l, user):
        global tuto, worlds, cout, selected, sizex, sizey, stat, tech
        tuto = ''
        if user:
            if w < len(Uworlds) and l < len(Uworlds[w]) and Uworlds[w][l].has_key("element"):
                self.load(Uworlds[w][l])
            else:
                self.load(worlds[w][l])
        else:
            self.load(worlds[w][l])
        sizex = len(world_new)
        sizey = len(world_new[0])
        resize();
        stat = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        over = 0
        infos()


    def savelevel(self, w, l):
        global tuto, users, worlds, Uworlds, nom, descriptif, video, link, tech, cout, victory, current, cycle, nrj, rayon, temp, maxcycle, maxnrj, maxrayon, maxtemp, world_new, world_art
        while len(Uworlds) <= w:
            Uworlds.append(0)
            Uworlds[w] = []
        while len(Uworlds[w]) <= l:
            Uworlds[w].append({})
            Uworlds[w][l] = {'nom': nom,
                         'element': element,
                         'users': users,
                         'tuto': tuto,
                         'description': descriptif,
                         '_xx': worlds[world][level]['_xx'],
                         '_yy': worlds[world][level]['_yy'],
                         'video': video,
                         'link': link,
                         'level': level,
                         'world': world,
                         'tech': tech,
                         'cout': cout,
                         'victory': victory,
                         'current': worlds[world][level]['current'],
                         'cycle': cycle,
                         'nrj': nrj,
                         'rayon': rayon,
                         'temp': temp,
                         'maxcycle': maxcycle,
                         'maxnrj': maxnrj,
                         'maxrayon': maxrayon,
                         'maxtemp': maxtemp,
                         'world_new': world_new,
                         'world_art': world_art}


''' *********************************************************************************************** '''
''' initialisation																		'''
global worlds, debug, level,inc
debug = 0
worlds = {}
world = level = 0
inout=io()
inout.verifyhome()
inout.read("dbdata")
inout.read(inout.gethome() + "/dbdata")
inout.reference(worlds, ['world', 'level'])
inout.reference(Uworlds, ['world', 'level'])
if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    debug = 1
else:
    debug = 0
inc=1


''' *********************************************************************************************** '''
''' Gestion du plateau de jeu																						 '''

#Classe du plateau de jeu
class game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(game, self).__init__(resizable=True, fullscreen=False, visible=True,
                                   caption="Wirechem: The new chemistry game")
        self.batch = pyglet.graphics.Batch()
        self.clocks = [clock.schedule(self.draw)]
        self.labels = []

    def draw(self, dt):
        glClearColor(0, 0, 0, 255)
        self.clear()

''' *********************************************************************************************** '''
''' Gestion lancement de la video																						 '''

#Classe du menu principal
class video(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(video, self).__init__(width=1024, height=768, resizable=True, fullscreen=False, visible=True,
                                   caption="Wirechem: The new chemistry game")
        self.player = pyglet.media.Player()
        self.player.queue(pyglet.resource.media("movie/intro.mp4"))
        self.player.play()
        self.clocks = clock.schedule(self.draw)

    def draw(self,dt):
        if self.player.source and self.player.source.video_format:
            glColor3ub(255,255,255)
            self.player.get_texture().blit(0,0,width=self.width,height=self.height)

    def on_key_press(self, symbol, modifiers):
        self.player.next()
        super(video, self).close()

    def on_mouse_press(self, x, y, button, modifiers):
        self.player.next()
        super(video, self).close()

''' *********************************************************************************************** '''
''' Gestion du menu principal																						 '''

#Classe du menu principal
class menu(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        global debug, worlds, world
        super(menu, self).__init__(width=1024, height=768, resizable=True, fullscreen=False, visible=True,
                                   caption="Wirechem: The new chemistry game")
        self.focus = None
        self.set_mouse_cursor(cursors['pointer'])
        self.batch = pyglet.graphics.Batch()
        self.p0 = pyglet.graphics.OrderedGroup(0)
        self.p1 = pyglet.graphics.OrderedGroup(1)
        self.p2 = pyglet.graphics.OrderedGroup(2)
        self.p3 = pyglet.graphics.OrderedGroup(3)
        self.p4 = pyglet.graphics.OrderedGroup(4)
        self.clocks = [clock.schedule(self.draw), clock.schedule_interval(self.movefond, 0.03)]
        self.loc = [0, 0, 1, 1]
        self.selected = -1
        self.icons=[abutton(self, 740, 110, 120, 0, 'icon_0', active=True, hilite=False, visible=False, selected=False, content=pyglet.image.load('picture/cout.png'), text='test', typeof='icon',align='right', hint=' '),
                    abutton(self, 740, 65, 120, 0, 'icon_1', active=True, hilite=False, visible=False, selected=False, content=pyglet.image.load('picture/cycle.png'), text='test', typeof='icon',align='right', hint=' '),
                    abutton(self, 940, 110, 70, 0, 'icon_2', active=True, hilite=False,visible=False, selected=False, content=pyglet.image.load('picture/tech.png'), text='test', typeof='icon',align='right', hint=' '),
                    abutton(self, 940, 65, 70, 0, 'icon_3', active=True, hilite=False, visible=False, selected=False, content=pyglet.image.load('picture/rayon.png'), text='test', typeof='icon',align='right', hint=' '),
                    abutton(self, 850, 110, 70, 0, 'icon_4', active=True, hilite=False, visible=False, selected=False, content=pyglet.image.load('picture/temp.png'), text='test', typeof='icon',align='right', hint=' '),
                    abutton(self, 850, 65, 70, 0, 'icon_5', active=True, hilite=False, visible=False, selected=False, content=pyglet.image.load('picture/nrj.png'), text='test', typeof='icon',align='right', hint=' ')]
        self.images = [pyglet.image.load('picture/leveler0.png'), pyglet.image.load('picture/leveler1.png'),
                       pyglet.image.load('picture/leveler2.png'), pyglet.image.load('picture/leveler3.png'),
                       pyglet.image.load('picture/leveler4.png')]
        self.colors = [[0, 192, 244], [235, 118, 118], [5, 157, 60], [215, 33, 255], [201, 209, 98]]
        self.sizes = [(50, 70), (50, 50), (30, 70), (50, 60), (28, 68)]
        self.names=["e","e","q","e","e","e","e","K","L","M","N","n","p"]
        self.thecolors=[[0, 0, 255],[50, 50, 200],[44, 120, 44],[60, 60, 60],[40, 40, 40],[200, 50, 50],[150, 50, 50],[50, 50, 200],[50, 50, 200],[50, 50, 200],[50, 50, 200],[122, 49, 25],[75, 119, 157]]

        #self.fond=pyglet.image.TileableTexture.create_for_image(image.load("picture/fond.png"))
        self.labels = [pyglet.text.Label("", font_name='vademecum', font_size=380, x=0, y=0, bold=False, italic=False,
                                         batch=self.batch, group=self.p0, color=(255, 80, 80, 230))]
        self.fond = image.load("picture/fond.png")
        self.rects = [arect(self,740,148,1016,8,1,[40,40,40,255],self.p1),
	                  arect(self,8,8,1017,149,2,[90,90,90,170],self.p0)]
        self.buttons = [
            abutton(self, 185, 'self.window.height-200', 0, 0, 'logo', active=True, hilite=False, visible=True, selected=False, content=pyglet.image.load('picture/logo.png'), text='', typeof='icon', hint=''),
            abutton(self, 45, 'self.window.height-150', 0, 0, 'logo2', active=True, hilite=False, visible=True, selected=False, content=pyglet.image.load('picture/logo2.png'), text='', typeof='icon', hint=''),
            abutton(self, 840, 150, 0, 0, 'menu_0', active=True, hilite=False, visible=True, selected=False, content=pyglet.image.load('picture/arrows.png'),text='', typeof='icon', hint=''),
            abutton(self, 920, 150, 0, 0, 'menu_1', active=True, hilite=False, visible=True, selected=False, content=pyglet.image.load('picture/arrows2.png'),text='', typeof='icon', hint=''),
            abutton(self, 940, 'self.window.height-100', 0, 0, 'menu_2', active=True, hilite=False, visible=True, selected=False, content=pyglet.image.load('picture/exit2.png'), text='', typeof='icon', hint='')
        ]
        self.infos = [atext(self, 12, 8, 730, 140, text="c un test", font='OpenDyslexicAlta', size=15)]
        self.infos[0].layout.begin_update()
        self.infos[0].color=(255,255,255,255)
        self.infos[0].layout.document.set_style(0, len(self.infos[0].layout.document.text), dict(align="left"))
        self.infos[0].layout.end_update()
        self.infos[0].text=" "
        self.infos[0].update(0)
        self.victorys = [abutton(self, 740+21*i, 12, 21, 38, 'victory_'+str(i), active=True, hilite=False, visible=True, selected=False, content=self.thecolors[i], text='test', typeof='color', hint=self.names[i]+"\n0")  for i in range(len(self.names))]
        for i in range(len(self.names)):
            self.victorys[i].layout.document.set_style(0,2,dict(font_name="Mechanihan", font_size=10, color=(180,180,180,255), align="left"))
            self.victorys[i].layout.document.set_style(1,1,dict(font_name="Mechanihan", font_size=14, bold=True ,color=(180,180,180,255), align="left"))
            self.victorys[i].layout.content_valign="top"
            self.levels = [abutton(self, -250, 0, 0, 0, 'level_'+str(i), active=True, hilite=False, visible=True, selected=False, content=self.images[level], text='test', typeof='icon', hint='')  for i in range(10)]
            self.untitled2 = [atext(self, -300, -300, 300, 0, text="", font='Fluoxetine', size=18) for i in range(10)]
            self.untitled = [atext(self, -300, -300, 60, 0, text="", font='Vademecum', size=23) for i in range(10)]
            self.special = pyglet.sprite.Sprite(pyglet.image.load('picture/boss.png'), batch=self.batch, group=self.p4,x=-300, y=-300)
            self.lock = [pyglet.sprite.Sprite(pyglet.image.load('picture/locked.png'), batch=self.batch, group=self.p4, x=-300, y=-300) for i in range(10)]
            self.update(0)

    def on_resize(self, width, height):
        super(menu, self).on_resize(width, height)
        try:
            self.update(0)
        except:
            dummy=0

    def movefond(self, dt):
        global loc
        self.loc[0] += self.loc[2]
        self.loc[1] += self.loc[3]
        if self.loc[0] > 1024:
            self.loc[2] = -1
        if self.loc[1] > 768:
            self.loc[3] = -1
        if self.loc[0] < 0:
            self.loc[2] = 1
        if self.loc[1] < 0:
            self.loc[3] = 1

    def update(self,alevel):
        global world, worlds, finished
        for obj in worlds[world]:
            if obj.has_key('special'):
                break
        if 'obj' in locals(): self.labels[0].text = obj['element']
        self.labels[0].color = (self.colors[world][0], self.colors[world][1], self.colors[world][2], 100)
        self.labels[0].x = (1024 - self.labels[0].content_width) / 2 - 50
        self.labels[0].y = 75 * self.height / 768
        if 'obj' in locals():
            self.labels[0].text = obj['element']
        else:
            self.labels[0].text = ''
        for l in range(len(self.buttons)):
            if alevel!=0 and alevel!=l: continue
            self.buttons[l].update(0)
        for l in range(10):
            if alevel!=0 and alevel!=l: continue
            if l >= len(worlds[world]):
                self.levels[l].x = -300
                self.untitled[l].x = -300
                self.untitled2[l].x = -300
                self.lock[l].x = -300
                self.levels[l].update(0)
                self.untitled2[l].update(0)
                self.untitled[l].update(0)
                continue
            ele = worlds[world][l]
            self.levels[l].active = (world, l) in finished or debug == 2
            self.levels[l].x = ele['_xx']
            self.levels[l].y = ele['_yy'] / 768.0 * self.height
            self.levels[l].setselected(
                [255, 120 + int(ele['_xx'] / 1024.0 * 135), 155 + int(ele['_xx'] / 1024.0 * 100)])
            self.levels[l].content = self.images[world]
            self.levels[l].update(0)
            self.untitled[l].text = ele['element']
            self.untitled[l].x = ele['_xx'] + (self.images[world].width - 60) / 2
            self.untitled[l].y = ele['_yy'] / 768.0 * self.height + 18
            self.untitled[l].loaded = 'worlds[' + str(world) + '][' + str(l) + ']["element"]'
            self.untitled[l].color = (
            int(ele['_xx'] / 1024.0 * 150), int(ele['_xx'] / 1024.0 * 150), int(ele['_xx'] / 1024.0 * 150), 255)
            self.untitled[l].update(0)
            self.untitled2[l].text = ele['nom'].decode('utf-8')
            self.untitled2[l].x = ele['_xx'] + (self.images[world].width - 300) / 2
            self.untitled2[l].y = ele['_yy'] / 768.0 * self.height - 25
            self.untitled2[l].loaded = 'worlds[' + str(world) + '][' + str(l) + ']["nom"]'
            if (world, l) in finished or debug == 2:
                self.untitled2[l].color = (255, 255, 255, 255)
            else:
                self.untitled2[l].color = (90, 90, 90, 255)
            self.untitled2[l].update(0)
            self.lock[l].visible = (world, l) not in finished and not debug == 2
            self.lock[l].x = ele['_xx'] + 10
            self.lock[l].y = ele['_yy'] / 768.0 * self.height + 50
            if 'obj' in locals() and ele['description'] == obj['description']:
                self.special.x = ele['_xx']
                self.special.y = ele['_yy'] / 768.0 * self.height
        if 'obj' not in locals():
            self.special.x = -300

    def drawLaser(self, x1, y1, x2, y2, width, power, color, randomize):
        while (width > 0):
            if randomize != 0: glLineStipple(random.randint(0, randomize), random.randint(0, 65535))
            glLineWidth(width)
            glBegin(GL_LINES)
            glColor3ub(min(color[0] + power * width, 255), min(color[1] + power * width, 255),
                       min(color[2] + power * width, 255))
            glVertex2i(x1, y1)
            glVertex2i(x2, y2)
            width = width - 1
            glEnd()
            glLineStipple(1, 65535)

    def draw(self, dt):
        global loc, world, worlds, thex, they, debug
        glClear(GL_COLOR_BUFFER_BIT);
        #self.fond.anchor_x=self.loc[0]
        #self.fond.anchor_y=self.loc[1]
        if debug < 2:
            glColor4ub(255, 255, 255, 160)
            self.fond.blit(self.loc[0], self.loc[1])
            self.fond.blit(self.loc[0] - 1024, self.loc[1])
            self.fond.blit(self.loc[0] - 1024, self.loc[1] - 768)
            self.fond.blit(self.loc[0], self.loc[1] - 768)
        #self.fond.blit_tiled(0, 0, 0, self.width, self.height)
        for ele in worlds[world]:
            for n in ele['link']:
                if world == n[0]:
                    src = (int(ele['_xx'] + self.images[0].width / 2),
                           int(ele['_yy'] / 768.0 * self.height + self.images[0].height / 2))
                    dest = (int(worlds[n[0]][n[1]]['_xx'] + self.images[0].width / 2),
                            int(worlds[n[0]][n[1]]['_yy'] / 768.0 * self.height + self.images[0].height / 2))
                else:
                    src = (int(ele['_xx'] + self.images[0].width / 2),
                           int(ele['_yy'] / 768.0 * self.height + self.images[0].height / 2))
                    dest = (int(1024), int(worlds[n[0]][n[1]]['_yy'] / 768.0 * self.height + 50))
                if dest[0] - src[0] != 0:
                    angle = math.atan(float(dest[1] - src[1]) / float(dest[0] - src[0]))
                else:
                    angle = 270 * 3.14 / 180.0
                if dest[0] - src[0] < 0:
                    angle = angle + 180 * 3.14 / 180.0
                src = (src[0] + int(self.sizes[world][0] * math.cos(angle)),
                       src[1] + int(self.sizes[world][1] * math.sin(angle)))
                if world == n[0]:
                    dest = (dest[0] - int(self.sizes[world][0] * math.cos(angle)),
                            dest[1] - int(self.sizes[world][1] * math.sin(angle)))
                if n in finished or debug == 2:
                    params = (random.randint(0, 8), 20, self.colors[world], 12)
                else:
                    params = (2, 20, [40, 40, 40], 0)
                self.drawLaser(src[0], src[1], dest[0], dest[1], params[0], params[1], params[2], params[3])
                if debug == 2 and world == n[0]:
                    if dest[0] - src[0] != 0:
                        angle = math.atan(float(dest[1] - src[1]) / float(dest[0] - src[0]))
                    else:
                        angle = 270 * 3.14 / 180.0
                    if dest[0] - src[0] < 0:
                        angle = angle + 180 * 3.14 / 180.0
                    self.drawLaser(dest[0], dest[1], dest[0] - int(20 * math.cos(angle + 30 * 3.14 / 180)),
                                   dest[1] - int(20 * math.sin(angle + 30 * 3.14 / 180)), params[0], params[1],
                                   params[2], params[3])
                    self.drawLaser(dest[0], dest[1], dest[0] - int(20 * math.cos(angle - 30 * 3.14 / 180)),
                                   dest[1] - int(20 * math.sin(angle - 30 * 3.14 / 180)), params[0], params[1],
                                   params[2], params[3])
        if world > 0:
            for ele in worlds[world - 1]:
                for n in ele['link']:
                    if n[0] == world:
                        src = (int(0), int(worlds[n[0]][n[1]]['_yy'] / 768.0 * self.height + self.images[0].height / 2))
                        dest = (int(worlds[n[0]][n[1]]['_xx'] + self.images[0].width / 2),
                                int(worlds[n[0]][n[1]]['_yy'] / 768.0 * self.height + self.images[0].height / 2))
                        if dest[0] - src[0] != 0:
                            angle = math.atan(float(dest[1] - src[1]) / float(dest[0] - src[0]))
                        else:
                            angle = 270 * 3.14 / 180.0
                        if dest[0] - src[0] < 0:
                            angle = angle + 180 * 3.14 / 180.0
                        dest = (dest[0] - int(self.sizes[world][0] * math.cos(angle)),
                                dest[1] - int(self.sizes[world][1] * math.sin(angle)))
                        if n in finished or debug == 2:
                            params = (random.randint(0, 8), 20, self.colors[world], 12)
                        else:
                            params = (2, 20, [40, 40, 40], 0)
                        self.drawLaser(src[0], src[1], dest[0], dest[1], params[0], params[1], params[2], params[3])

        if type(self.selected) is tuple:
            if self.selected[0] == world:
                self.drawLaser(int(worlds[self.selected[0]][self.selected[1]]['_xx'] + self.images[0].width / 2), int(
                    worlds[self.selected[0]][self.selected[1]]['_yy'] / 768.0 * self.height + self.images[
                        0].height / 2), int(thex), int(they), random.randint(0, 8), 20, self.colors[world], 12)
            else:
                self.drawLaser(int(0), int(
                    worlds[self.selected[0]][self.selected[1]]['_yy'] / 768.0 * self.height + self.images[
                        0].height / 2), int(thex), int(they), random.randint(0, 8), 20, self.colors[world], 12)
        self.batch.draw()

    ### Evenement générer par classe abutton ###

    def on_mouse_press_logo(self, state):
        global debug
        if debug == 1:
            debug = 2
            ambiance.pause()
            self.buttons[0].setselected([255, 0, 0])
        elif debug == 2:
            self.infos[0].loaded=""
            self.infos[0].text=" "
            self.infos[0].update()
            debug = 1
            self.buttons[0].setselected(False)
            ambiance.play()
        self.update(0)

    def on_mouse_double_logo2(self, state):
        global debug
        if debug == 2:
            inout.rebase()
            self.on_mouse_press_logo(self)

    def on_mouse_press_menu_2(self, state):
        pyglet.app.exit()

    def on_mouse_press_menu_1(self, state):
        global world
        if world > 0:
            world -= 1
            self.update(0)
            sounds.next()
            sounds.queue(pyglet.resource.media("sound/lightning3.wav"))
            sounds.play()

    def on_mouse_press_menu_0(self, state):
        global world
        if world < len(worlds) - 1:
            world += 1
            self.update(0)
            sounds.next()
            sounds.queue(pyglet.resource.media("sound/lightning1.wav"))
            sounds.play()

    def on_mouse_enter_menu(self, n, state):
        self.buttons[2 + n].setselected([255, 0, 0])

    def on_mouse_double_level(self, n, state):
        if debug < 2:
            return
        for ele in worlds[world]:
            try:
                del ele['special']
            except:
                dummy = 0
        worlds[world][n]["special"] = True
        self.update(n)

    def on_mouse_drag_level(self, n, state):
        global worlds, world
        if debug < 2:
            return
        if state['buttons'] == 2:
            worlds[world][n]["_xx"] += state['dx']
            worlds[world][n]["_yy"] += state['dy']
            self.set_mouse_cursor(cursors['move'])
            self.update(n)
        elif (state['buttons'] == 1 or state['buttons'] == 4) and type(self.selected) is int:
            self.selected = (world, n)
            self.set_mouse_cursor(cursors['create'])

    def on_mouse_release_level(self, n, state):
        global worlds, world
        if debug < 2:
            return
        if state['buttons'] == 1 and type(self.selected) is tuple and n != self.selected[1]:
            try:
                worlds[world][n]["link"].index(self.selected) == -1
            except:
                try:
                    worlds[world][self.selected]["link"].index((self.selected[0], n)) == -1
                except:
                    worlds[self.selected[0]][self.selected[1]]["link"].append((world, n))
                    self.selected = -1
        elif state['buttons'] == 4 and type(self.selected) is tuple and n != self.selected:
            try:
                worlds[world][n]["link"].remove(self.selected)
            except:
                dummy = 0
            try:
                worlds[self.selected[0]][self.selected[1]]["link"].remove((world, n))
            except:
                dummy = 0
        else:
            self.selected = -1
            self.set_mouse_cursor(cursors['pointer'])

    def on_mouse_leave_menu(self, n, state):
        self.buttons[2 + n].setselected(False)

    def on_mouse_enter_level(self, n, state):
        global world,worlds,level
        sounds.next()
        sounds.queue(pyglet.resource.media("sound/pickup1.wav"))
        sounds.play()
        level=n
        if debug == 2:
            for theicon in self.icons: theicon.hide()
            for theicon in self.untitled2:
                theicon.color = (255, 255, 255, 255)
                theicon.update()
            for i in range(len(self.levels)):
                self.levels[i].setselected([255, 120 + int(self.levels[i].x / 1024.0 * 135), 155 + int(self.levels[i].x / 1024.0 * 100)])
        self.levels[n].setselected([255, 0, 0])
        self.untitled2[n].color = (255, 0, 0, 255)
        self.untitled2[n].update()
        self.infos[0].text=worlds[world][n]['description'].decode('utf-8')
        self.infos[0].loaded='worlds[' + str(world) + '][' + str(n) + ']["description"]'
        self.infos[0].update()
        var=['cout','maxcycle','tech','maxrayon','maxtemp','maxnrj']
        condition=[worlds[world][n]['cout']>0,worlds[world][n]['maxcycle']<90000,worlds[world][n]['tech']>0,worlds[world][n]['maxrayon']<90000,worlds[world][n]['maxtemp']<90000,worlds[world][n]['maxnrj']<90000]
        for i in range(len(condition)):
            if debug==2 or condition[i]:
                if worlds[world][n][var[i]]<90000:
                    self.icons[i].text=str(worlds[world][n][var[i]])
                else:
                    self.icons[i].text="illimite"
                self.icons[i].show()
            else:
                self.icons[i].hide()

    def on_mouse_double_icon(self, n, state):
        global world,worlds,level,inc
        var=['cout','maxcycle','tech','maxrayon','maxtemp','maxnrj']
        if var[n]=='tech':
            return
        if worlds[world][level][var[n]]<90000:
            worlds[world][level][var[n]]=90001
            self.icons[n].text="illimite"
        else:
            worlds[world][level][var[n]]=0
            self.icons[n].text=str(0)
        self.icons[n].update(0)


    def on_mouse_press_icon(self, n, state):
        global inc
        if inc==1:
            inc=10
        elif inc==10:
            inc=100
        elif inc==100:
            inc=1000
        else:
            inc=1

    def on_mouse_scroll_icon(self, n, state):
        global world,worlds,level,inc
        var=['cout','maxcycle','tech','maxrayon','maxtemp','maxnrj']
        add=state['dy']*inc
        if worlds[world][level][var[n]]<90000:
            print add
            worlds[world][level][var[n]]=worlds[world][level][var[n]]+add
            if var[n]=='tech':
                if worlds[world][level]['tech']<-1: worlds[world][level]['tech']=-1
                if worlds[world][level]['tech']>9: worlds[world][level]['tech']=9
            else:
                if worlds[world][level][var[n]]<0: worlds[world][level][var[n]]=0
            self.icons[n].text=str(worlds[world][level][var[n]])
            self.icons[n].update(0)

    def on_mouse_leave_level(self, n, state):
        if debug == 2:
            return
        self.levels[n].setselected(
            [255, 120 + int(self.levels[n].x / 1024.0 * 135), 155 + int(self.levels[n].x / 1024.0 * 100)])
        self.untitled2[n].color = (255, 255, 255, 255)
        self.untitled2[n].update()
        self.infos[0].loaded=""
        self.infos[0].text=" "
        self.infos[0].update()
        for theicon in self.icons: theicon.hide()

    def on_mouse_press_level(self, n, state):
        global level
        if debug == 2:
            self.selected = -1
            if state['modifiers'] & key.MOD_CTRL:
                del worlds[world][n]
                self.update(0)
                for ele in worlds[world]:
                    l = 0
                    while l < len(ele['link']):
                        element = ele['link'][l][1]
                        if ele['link'][l][0] == world:
                            if element > n: element -= 1
                            if element != n:
                                ele['link'][l] = (ele['link'][l][0], element)
                                l += 1
                            else:
                                del ele['link'][l]
                        else:
                            l += 1
            return
        else:
            level=n
            super(menu,self).close()
            thegame=game()
            thegame.set_minimum_size(1024, 768)
            pyglet.app.run()


        ### Evenement de la fenetre ###

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        global thex, they, world, worlds
        if debug < 2:
            return
        if type(self.selected) is tuple:
            thex = x
            they = y
        if x > 1024 - 20 and world + 1 < len(worlds) and abs(self.selected[0] - world) < 1:
            world += 1
            self.update(0)
            return
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if debug < 2:
            return
        self.selected = -1

    def on_mouse_press(self, x, y, button, modifiers):
        if debug < 2:
            return
        if modifiers & key.MOD_SHIFT and len(worlds[world]) < 10:
            worlds[world].append({'nom': 'nouveau',
                                  'description': "niveau tout neuf. " + str(random.randint(0, 255)),
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
                                  '_xx': x - self.images[0].width / 2,
                                  '_yy': y * 768 / self.height - self.images[0].height / 2,
                                  'link': [],
                                  'video': False,
                                  'world_art': [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                  'world_new': [[0, 0, 0], [0, 0, 0], [0, 0, 0]]})
            self.update(len(worlds[world])-1)
            return
        for widget in self.untitled2 + self.untitled + self.infos:
            if widget.hit_test(x, y):
                self.setfocus(widget)
                break
        else:
            self.setfocus(None)
        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if debug < 2:
            return
        for widget in self.untitled2 + self.untitled + self.infos:
            if widget.hit_test(x, y):
                self.set_mouse_cursor(cursors['text'])
                break
        else:
            self.set_mouse_cursor(cursors['pointer'])

    def on_text(self, text):
        if debug < 2:
            return
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if debug < 2:
            return
        if self.focus:
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if debug < 2:
            return
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if debug < 2:
            return
        if modifiers & key.MOD_SHIFT:
            self.set_mouse_cursor(cursors['cross'])
        elif modifiers & key.MOD_CTRL:
            self.set_mouse_cursor(cursors['delete'])
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1
            all=(self.untitled2 + self.untitled + self.infos)
            if self.focus in all:
                i = all.index(self.focus)
            else:
                i = 0
                dir = 0
            self.setfocus(all[(i + dir) % len(all)])
        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

    def setfocus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0
        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)


''' *********************************************************************************************** '''
''' Lancement du menu principal																					'''

cursors = {'pointer':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/pointer.png'), 15, 46),
           'text':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/text.png'), 24, 30),
           'move':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/move.png'), 24, 24),
           'create':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/create.png'), 12, 17),
           'cross':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/cross.png'), 24, 33),
           'delete':pyglet.window.ImageMouseCursor(pyglet.resource.image('cursor/delete.png'), 24, 32)}
pyglet.font.add_file('font/Fluoxetine.ttf')
pyglet.font.add_file('font/OpenDyslexicAlta.otf')
pyglet.font.add_file('font/Mecanihan.ttf')
pyglet.font.add_file('font/Vademecum.ttf')
pyglet.font.add_file('font/LiberationMono-Regular.ttf')
ambiance = pyglet.media.Player()
ambiance.queue(pyglet.resource.media("music/ambiance1.mp3"))
ambiance.volume = 0.1
ambiance.eos_action = 'loop'
ambiance.play()
sounds = pyglet.media.Player()
sounds.volume = 0.6
video_intro=video()
pyglet.app.run()
menu_principal = menu()
menu_principal.set_minimum_size(1024, 768)
glEnable(GL_BLEND);
#glEnable(GL_STENCIL_TEST);
#glEnable(GL_LINE_SMOOTH);
#glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST);
glEnable(GL_LINE_STIPPLE)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
pyglet.app.run()






