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

**Fonctions d'attente**

####WAIT

Attend un clic ou un appui sur une touche.

####WAIT sec

Attend le nombre de seconde spécifiés.

####WAIT MENU,menu,element

Attend le click sur le menu.

####WAIT DRAG,[bouton]

Attend un déplacement de curseur avec le bouton appuyé, il est possible
de préciser lequel.

####WAIT CLICK,[bouton]

Attend un clic du bouton précisé ou n'importe quel bouton si non précisé

**Fonctions d'affichage**

####MSG message

envoie un message à l'écran avec mise en forme. Les virgules doivent être
remplacées par des points virgules.

####RECT x1,y1,x2,y2

dessine un carré rouge pour attirer l'attention de l'utilisateur sur une
zone à l'écran dont les coordonnées sont spécifiées. Il ne peut y avoir
qu'un rectangle ou fléche à l'écran : choisissez !

####ARROW x1,y1,x2,y2

dessine une flèche rouge pour attirer l'attention de l'utilisateur sur 
une zone à l'écran dont les coordonnées sont spécifiées. Il ne peut y 
avoir qu'un rectangle ou fléche à l'écran : choisissez !

####DEL

efface tout ce qui a été dessiné à l'écran. Flèche, rectangle et message 
texte.

**Fonctions menu**

####MENU menu,element,button

Clique sur un élément de menu.

####SELECT menu,element,button

Choisi un élément de menu.

####SET menu,element    ou UNSET

Met en clignotance un élément du menu.

####UNSET menu,element

Retire la clignotance d'un élément du menu.

**fonctions gameplay**

####NEXT

Fait la prochaine génération de la grille de simulation.

####TECH niveau

Change le niveau technologique.

**fonction souris**

####CLICK x,y,button

Simule un clique sur le plateau de jeu aux coordonnées x,y.

####DRAG x1,y1,x2,y2,button

Simule un clique sur le plateau de jeu entre les coordonnées fournies.

