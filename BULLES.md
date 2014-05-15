----------------------------------------------------------------
##    WireChem

![The new chemistry game](logo.png)

http://wirechem.dahut.fr

*(C) Copyright 2013-2014 Nicolas Hordé
  Licence GPL V3.0*

----------------------------------------------------------------
###  Langage pour la création de Tutoriel

Les coordonnées sont celles du 1024x768 avec interpolation selon la 
resolution choisie. Les commandes sont insensibles à la casse.

*Fonctions d'attente*

####WAIT

Attend un click ou un appuie sur une touche.

####WAIT sec

Attend le nombre de seconde spécifiés.

####WAIT MENU,menu,element

Attend le click sur le menu.

####WAIT DRAG,[bouton]

Attend un deplacement de curseur.

####WAIT CLICK,[bouton]

Attend un click du bouton.

*Fonctions d'affichage*

####MSG message

envoie un message à l'écran avec mise en forme.

####RECT x1,y1,x2,y2

dessine un carré rouge pour attirer l'attention de l'utilisateur sur une
zone à l'écran dont les coordonnées sont spécifiées.

####ARROW x1,y1,x2,y2

dessine une flèche rouge pour attirer l'attention de l'utilisateur sur une
zone à l'écran dont les coordonnées sont spécifiées.

####DEL

efface tout ce qui a été dessiné à l'écran.

*Fonctions menu*

####MENU menu,element,button

Clique sur un élément de menu.

####SELECT menu,element,button

Choisi un élément de menu.

####SET menu,element    ou UNSET

Met en surbrillance un élément du menu.

####UNSET menu,element

Retire la surbrillance d'un élément du menu.

*fonctions gameplay*

####NEXT

Fait la prochaine génération de la grille de simulation.

####TECH niveau

Change le niveau technologique.

*fonction souris*

####CLICK x,y,button

Simule un clique sur le plateau de jeu aux coordonnées x,y.

####DRAG x1,y1,x2,y2,button

Simule un clique sur le plateau de jeu entre les coordonnées fournies.

