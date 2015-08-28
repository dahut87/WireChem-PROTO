#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
  ------------------------------------------
  
  Microlinux
  
  Classes OpenGl

  (C) Copyright 2013-2014 Nicolas Hordé
  
  ------------------------------------------
'''
import datetime
import math
import copy
import random
import time
import operator

import pyglet
from GLclass import *
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key
from pyglet import clock
from pyglet import image

''' *********************************************************************************************** '''
''' Classes graphiques																			    '''

#Classe comme un label avec l'attribut visible
class alabel(pyglet.text.Label):
    def __init__(self, window, xx, yy, visible=True, text="", font="Deja vu sans", size=16, group=None):
        self.window = window
        self.font=font
        self.size=size
        self.visible = visible
        super(alabel, self).__init__(text,x=xx,y=yy,font_name=self.font,font_size=self.size,group=group,batch=self.window.batch)
        self.update(0)

    def update(self,dt):
        if not self.visible:
            if self.x!=10000:
                self.xx=self.x
            self.x=10000
        else:
            if self.x==10000:
                self.x=self.xx
        self.font_size=self.size
        self.font_name=self.font

# Classe d'un rectangle
class arect(object):
    def __init__(self, window, x, y, width, height, visible=True, typeof=0, color=(180, 180, 180, 255), group=None):
        self.window = window
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.typeof = typeof
        self.color = color
        self.group = group
        self.visible = visible
        self.update(0)

    def update(self,dt):
        try:
            self.vertex_list.delete()
        except:
            foo = 0
        try:
            self.vertex_list2.delete()
        except:
            foo = 0
        if self.visible and (self.typeof == "face" or self.typeof == "both"):
            self.vertex_list = self.window.batch.add(4, pyglet.gl.GL_QUADS, self.group, (
            'v2i', [self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height]),
                                                     ('c4B', self.color * 4))
        if self.visible and self.typeof == "line" or self.typeof == "both":
            self.vertex_list2 = self.window.batch.add(4, pyglet.gl.GL_LINE_LOOP, self.group,
                                                      ('v2i',
                                                       [self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height]),
                                                      ('c3B', [self.color[0], self.color[1], self.color[2]] * 4))

#Classe d'un texte editable
class atext(object):
    def __init__(self, window, x, y, width, height, visible=True, text="", font="Deja vu sans", size=10, align="center", color=(180, 180, 180, 255)):
        self.evalx = x
        self.evaly = y
        self.x = x
        self.y = y
        self.window = window
        if type(self.evalx) is str:
            self.x = eval(self.evalx)
        if type(self.evaly) is str:
            self.y = eval(self.evaly)
        self.loaded = ''
        self.align = align
        self.font = font
        self.size = size
        self.text = text
        self.color = color
        self.height = height
        self.visible = visible
        self.document = pyglet.text.document.FormattedDocument(text.decode("utf8"))
        self.document.set_style(0, len(self.document.text),dict(font_name=self.font, font_size=self.size, color=self.color, align=self.align,
                                     background_color=(200, 200, 200, 0)))
        if height == 0:
            font = self.document.get_font(0)
            height = font.ascent - font.descent
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, width, height, multiline=True,
                                                               batch=self.window.batch, group=self.window.p3)
        self.layout.document.register_event_type('self.on_insert_text')
        self.layout.on_layout_update = self.on_layout_update
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.visible = False
        self.update(0)

    def update(self,dt):
        self.layout.begin_update()
        if type(self.evalx) is str:
            self.x = eval(self.evalx)
        if type(self.evaly) is str:
            self.y = eval(self.evaly)
        if self.visible:
            self.layout.x = self.x
        else:
            self.layout.x = 10000
        self.layout.y = self.y
        #self.layout.document.text = self.text.decode('utf8')
        if len(self.layout.document.text) > 0:
            self.layout.document.set_style(0, len(self.layout.document.text),
                                dict(font_name=self.font, font_size=self.size, color=self.color, align=self.align,
                                     background_color=(200, 200, 200, 0)))
        self.layout.end_update()

    def on_layout_update(self):
        if self.loaded != '':
            #exec (self.loaded + '="' + self.layout.document.text + '"')
            self.text = self.layout.document.text

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and 0 < y - self.layout.y < self.layout.height)


#Bouton sensible a plusieurs évènements, types: function, multicon, icon, color,
#                                                                             et text in,left,top,bottom,right
class abutton(object):
    def update(self, dt):
        if not self.hilite and dt>0:
            return
        try:
            self.vertex_list.delete()
        except:
            foo = 0
        try:
            self.vertex_list2.delete()
        except:
            foo = 0
        try:
            self.vertex_list3.delete()
        except:
            foo = 0
        if type(self.evalx) is str:
            self.x = eval(self.evalx)
        if type(self.evaly) is str:
            self.y = eval(self.evaly)

        if self.typeof == 'color':
            if self.isvisible():
                if not self.isactive():
                    color = (self.content[0], self.content[1], self.content[2], 127)
                else:
                    color = (self.content[0], self.content[1], self.content[2], 255)
                self.vertex_list = self.window.batch.add(4, pyglet.gl.GL_QUADS, self.window.p1,
                                                         ('v2i', (self.x, self.y, self.x + self.width, self.y,
                                                                  self.x + self.width, self.y + self.height, self.x,
                                                                  self.y + self.height)),
                                                         ('c4B', color * 4))
        elif self.typeof == 'function':
            self.vertex_list = eval(self.content)
        else:
            if self.typeof == 'multicon':
                self.sprite.image = self.content[self.index]
            else:
                self.sprite.image = self.content
            self.sprite.visible=self.isvisible()
            if self.width == 0:
                self.width = self.sprite.image.width
            if self.height == 0:
                self.height = self.sprite.image.height
                if self.text!='':
                    self.layout.begin_update()
                    self.layout.document.text=self.text
                    self.layout.document.set_style(0, len(self.layout.document.text),dict(font_name=self.font, font_size=self.size))
                    self.layout.end_update()
                    if self.align=="top" or self.align=="bottom":
                        font = self.layout.document.get_font(0)
                        self.height+= font.ascent - font.descent
                    elif self.align=="left" or self.align=="right":
                        self.width+=self.layout.content_width
            if self.width / float(self.height) < self.sprite.image.width / float(self.sprite.image.height):
                self.sprite.scale = float(self.width) / self.sprite.image.width
            else:
                self.sprite.scale = float(self.height) / self.sprite.image.height
            self.sprite.x=self.x
            self.sprite.y=self.y
            if not self.isactive():
                self.sprite.color = (60, 60, 60)
            else:
                self.sprite.color = (255, 255, 255)
            if self.text != '':
                self.layout.begin_update()
                if not self.scale:
                    self.sprite.scale=1
                picalign="center"
                if not self.isvisible():
                    self.layout.x=10000
                elif self.align=="right":
                    self.sprite.x=self.x
                    self.sprite.y=self.y+(self.height-self.sprite.height)/2
                    self.layout.x=self.sprite.x+self.sprite.width
                    self.layout.width=self.width-self.sprite.width
                    self.layout.y=self.y
                    self.layout.height=self.height
                    self.layout.content_valign='center'
                    picalign="left"
                elif self.align=="left":
                    self.sprite.x=self.x+self.width-self.sprite.width
                    self.sprite.y=self.y+(self.height-self.sprite.height)/2
                    self.layout.x=self.x
                    self.layout.width=self.width-self.sprite.width
                    self.layout.y=self.y
                    self.layout.height=self.height
                    self.layout.content_valign='center'
                    picalign="right"
                elif self.align=="bottom":
                    self.sprite.x=self.x+(self.width-self.sprite.width)/2
                    self.sprite.y=self.y+self.height-self.sprite.height
                    self.layout.x=self.x
                    self.layout.width=self.width
                    self.layout.y=self.y
                    self.layout.height=self.height-self.sprite.height
                    self.layout.content_valign='top'
                elif self.align=="in":
                    self.sprite.x=self.x+(self.width-self.sprite.width)/2
                    self.sprite.y=self.y+(self.height-self.sprite.height)/2
                    self.layout.x=self.x
                    self.layout.y=self.y
                    self.layout.width=self.width
                    self.layout.height=self.height
                    self.layout.content_valign='center'
                else:
                    self.sprite.x=self.x+(self.width-self.sprite.width)/2
                    self.sprite.y=self.y
                    self.layout.x=self.x
                    self.layout.width=self.width
                    self.layout.y=self.y+self.sprite.height
                    self.layout.height=self.height-self.sprite.height
                    self.layout.content_valign='bottom'
                if len(self.layout.document.text)>0:
                    if type(self.selected) is not list:
                        if self.active:
                            piccolor=(90, 90, 90,255)
                        else:
                            piccolor=(180, 180, 180,255)
                    else:
                        piccolor=(self.selected[0], self.selected[1], self.selected[2], 255)
                    self.layout.document.set_style(0, len(self.layout.document.text),
                                dict(font_name=self.font, font_size=self.size, color=piccolor, align=picalign,
                                     background_color=(200, 200, 200, 0)))
                self.layout.end_update()
        if type(self.selected) is tuple:
            color = (self.selected[0], self.selected[1], self.selected[2], 255)
            self.vertex_list2 = self.window.batch.add(4, pyglet.gl.GL_LINE_LOOP, self.window.p2,
                                                      ('v2i', (
                                                      self.x, self.y, self.x + self.width, self.y, self.x + self.width,
                                                      self.y + self.height, self.x, self.y + self.height)),
                                                      ('c4B', color * 4))
        elif type(self.selected) is list and self.isactive():
            self.sprite.color = (self.selected[0], self.selected[1], self.selected[2])
        if self.hilite and int(time.time()) % 2 == 0:
            color = (255, 0, 0, 128)
            self.vertex_list3 = self.window.batch.add(4, pyglet.gl.GL_QUADS, self.window.p2,
                                                      ('v2i', (
                                                      self.x, self.y, self.x + self.width, self.y, self.x + self.width,
                                                      self.y + self.height, self.x, self.y + self.height)),
                                                      ('c4B', color * 4))

    def __init__(self, window, x, y, width, height, name, active=True, hilite=False, visible=True, selected=False, content=None, hint="", typeof="icon",
                 text="", align="left", font="Deja vu sans", size=16, scale=False):
        self.name = name
        self.time = 0
        self.index = 0
        self.enter = 0
        self.window = window
        self.evalx = x
        self.evaly = y
        self.x = x
        self.y = y
        self.scale=scale
        self.align=align
        self.font=font
        self.size=size
        self.width = width
        self.height = height
        self.active = active
        self.hilite = hilite
        self.visible = visible
        self.content = content
        self.typeof = typeof
        self.hint = hint
        self.text = text
        self.selected = selected
        self.window.push_handlers(self.on_mouse_press)
        self.window.push_handlers(self.on_mouse_motion)
        self.window.push_handlers(self.on_mouse_drag)
        self.window.push_handlers(self.on_mouse_release)
        self.window.push_handlers(self.on_mouse_scroll)
        self.updateclock = clock.schedule_interval(self.update, 1)
        if self.typeof=='multicon' or self.typeof=='icon':
            self.sprite = pyglet.sprite.Sprite(pyglet.image.Texture.create(1,1),x=-300,y=-300, batch=self.window.batch, group=self.window.p1)
        if self.text!='' or self.typeof=="text":
            self.layout = pyglet.text.layout.IncrementalTextLayout(pyglet.text.document.FormattedDocument(text), 10, 10, multiline=True, batch=self.window.batch, group=self.window.p2)
        self.update(0)

    def delete(self):
        try:
            self.vertex_list.delete()
        except:
            foo = 0
        try:
            self.vertex_list2.delete()
        except:
            foo = 0
        try:
            self.vertex_list3.delete()
        except:
            foo = 0
        try:
            self.sprite.delete()
        except:
            foo = 0

    def launch(self, state):
        name = self.name.split('_')
        if len(name) > 1 and hasattr(self.window, "on_mouse_" + state['event'] + "_" + name[0]) and callable(
                eval("self.window.on_mouse_" + state['event'] + "_" + name[0])):
            eval("self.window.on_mouse_" + state['event'] + "_" + name[0] + "(" + str(name[1]) + "," + str(state) + ")")
            #print state,self.name
        if hasattr(self.window, "on_mouse_" + state['event'] + "_" + self.name) and callable(
                eval("self.window.on_mouse_" + state['event'] + "_" + self.name)):
            if self.typeof == 'multicon':
                self.index += 1
                if self.index >= len(self.content):
                    self.index = 0
                self.update(0)
            eval("self.window.on_mouse_" + state['event'] + "_" + self.name + "(" + str(state) + ")")
            #print state,self.name

    def on_mouse_press(self, x, y, button, modifiers):
        if x > self.x and y > self.y and x < self.x + self.width and y < self.y + self.height and self.isactive() and self.isvisible():
            if time.time() - self.time < 0.30:
                state = {'x': x, 'y': y, 'dx': 0, 'dy': 0, 'buttons': button, 'modifiers': modifiers, 'event': 'double'}
                self.launch(state)
            self.time = time.time()
            state = {'x': x, 'y': y, 'dx': 0, 'dy': 0, 'buttons': button, 'modifiers': modifiers, 'event': 'press'}
            self.launch(state)

    def on_mouse_release(self, x, y, button, modifiers):
        if x > self.x and y > self.y and x < self.x + self.width and y < self.y + self.height and self.isactive() and self.isvisible():
            state = {'x': x, 'y': y, 'dx': 0, 'dy': 0, 'buttons': button, 'modifiers': modifiers, 'event': 'release'}
            self.launch(state)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if x > self.x and y > self.y and x < self.x + self.width and y < self.y + self.height and self.isactive() and self.isvisible():
            state = {'x': x, 'y': y, 'dx': dx, 'dy': dy, 'buttons': buttons, 'modifiers': modifiers, 'event': 'drag'}
            self.launch(state)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if x > self.x and y > self.y and x < self.x + self.width and y < self.y + self.height and self.isactive() and self.isvisible():
            state = {'x': x, 'y': y, 'dx': scroll_x, 'dy': scroll_y, 'buttons': 0, 'modifiers': 0, 'event': 'scroll'}
            self.launch(state)

    def on_mouse_motion(self, x, y, dx, dy):
        if x > self.x and y > self.y and x < self.x + self.width and y < self.y + self.height:
            if self.isvisible() and self.isactive():
                if self.enter == 0:
                    self.enter = 1
                    state = {'x': x, 'y': y, 'dx': dx, 'dy': dy, 'buttons': 0, 'modifiers': 0, 'event': 'enter'}
                    self.launch(state)
                state = {'x': x, 'y': y, 'dx': dx, 'dy': dy, 'buttons': 0, 'modifiers': 0, 'event': 'motion'}
                self.launch(state)
        else:
            if self.enter == 1:
                self.enter = 0
                state = {'x': x, 'y': y, 'dx': dx, 'dy': dy, 'buttons': 0, 'modifiers': 0, 'event': 'leave'}
                self.launch(state)

    def setselected(self, select):
        self.selected = select
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
            self.visible = False
            self.update(0)

    def show(self):
        if type(self.visible) is bool:
            self.visible = True
            self.update(0)

    def activate(self):
        if type(self.active) is bool:
            self.active = True
            self.update(0)

    def unactivate(self):
        if type(self.active) is bool:
            self.active = False
            self.update(0)

    def hilitate(self):
        if type(self.hilite) is bool:
            self.hilite = True
            self.update(0)

    def unhilitate(self):
        if type(self.hilite) is bool:
            self.hilite = False
            self.update(0)

# Classe interface
class ainter(abutton):
    def  __init__(self, window, x, y, icon, comment="", text="", cmd="", font="Deja vu"):
        if window.width>1800:
            super(ainter,self).__init__(window, x, y, 0, 0, "item_"+str(window.count), content=icon, hint=comment, typeof="icon", text=text, align="bottom", size=16, font=font, scale=False)
        elif window.width>1600:
            super(ainter,self).__init__(window, x, y, 96, 0, "item_"+str(window.count), content=icon, hint=comment, typeof="icon", text=text, align="bottom", size=14, font=font, scale=True)
        elif window.width>1280:
            super(ainter,self).__init__(window, x, y, 64, 0, "item_"+str(window.count), content=icon, hint=comment, typeof="icon", text=text, align="bottom", size=12, font=font, scale=True)
        else:
            super(ainter,self).__init__(window, x, y, 48, 0, "item_"+str(window.count), content=icon, hint=comment, typeof="icon", text=text, align="bottom", size=10, font=font, scale=True)
        self.cmd=cmd
        window.count+=1
