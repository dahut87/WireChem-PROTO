#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
  ------------------------------------------
  
  WireChem - The new chemistry game
  
  Programme lancement

  (C) Copyright 2013-2014 Nicolas Hordé
  Licence GPL V3.0
  
  ------------------------------------------
'''
import os;
while True:
	os.system("clear")
	print'''-------------------------------------------
  
  WireChem - The new chemistry game
  
  Menu principal

  (C) Copyright 2013-2014 Nicolas Hordé
  Licence GPL V3.0
  
  ------------------------------------------
  1) Lancer Wirechem depuis le CD/DVD
  2) Récupérer une version depuis le réseau
  3) Lancer une autre version 
  4) Eteindre l'ordinateur
  5) Redemarrer l'ordinateur
  '''
	alocal=raw_input('Que souhaitez vous faire ? : ')
	if alocal=="1":
		os.system('python WireChem.py')
	elif alocal=="2":
		os.system("clear")
		print "vérifiez que vous êtes bien connecté à internet..."
		print "Récupération des version depuis https://github.com/dahut87/WireChem.git..."
		tag=['master']
		tags=os.popen('git ls-remote --tags https://github.com/dahut87/WireChem.git').read().split('\n')
		for i in range(len(tags)):
			if tags[i][41:51]=='refs/tags/': tag.append(tags[i][51:].replace('^{}',''))
		tag=sorted(list(set(tag)),None,None,True)
		for i in range(len(tag)):
			print str(i)+") "+tag[i]
		alocal=raw_input(str(len(tag))+" versions trouvées, choisissez celle que vous souhaitez récupérer: ")
		if alocal=="": continue
		version=tag[int(alocal)]
		if os.system('git clone -b '+version+' https://github.com/dahut87/WireChem.git _version_'+version)==0:
				os.system("cd _version_"+version+" && python WireChem.py")
		else:
				alocal=raw_input("Une erreur est apparue, le dossier existe déjà ou vous n'êtes plus connecté ! Appuyer sur O pour essayer de lancer.")
				if alocal.lower()=="o":
					os.system("cd _version_"+version+" && python WireChem.py")
	elif alocal=="3":
		os.system("clear")
		print "Recherche des version déjà récupérée..."
		dir=os.listdir(".")
		num=0
		vers=[]
		for i in range(len(dir)):
			if dir[i][:9]=="_version_": 
				vers.append(dir[i])
				print str(num)+") "+dir[i][9:]
				num+=1
		if num==0:
			print "aucune version installée...<appuyez sur une touche>"
			raw_input()
		else:
			alocal=raw_input(str(num)+" versions trouvées, choisissez celle que vous souhaitez récupérer: ")
			if alocal=="": continue
			os.system("cd "+vers[int(alocal)]+" && python WireChem.py")
	elif alocal=="4":
		os.system("halt")
	elif alocal=="5":
		os.system("reboot")
