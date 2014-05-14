----------------------------------------------------------------
##    WireChem

![The new chemistry game](logo.png)

http://wirechem.dahut.fr

*(C) Copyright 2013-2014 Nicolas Hordé
  Licence GPL V3.0*

----------------------------------------------------------------
###  A faire !!!!

#### GAME PLAY
 
* Implémenter l'automate cellulaire "Sand" dans le déplacement des 
  protons & neutrons sur  le plateau de jeu.
* Ajouter une fenêtre qui s'affiche au changement de niveau 
technologique afin de présenter les nouveautés accessibles.
* Ajouter des bulles d'aide au survol des éléments de jeu afin d'
informer le joueur sur leur nature et leur état.
* Ajouter un véritable tutoriel.
* Ajouter un mode Pas a pas (liseré vert) qui permettra de passer pas a
pas le fonctionnement du modèle, la victoire n'est pas comptabilisé dans
ce mode, ajout d'un élément de menu pour le pas à pas.
* Ajouter un système avec des points de recherche acquis lors des 
changements de niveau (Niveau*50), avec il serait possible d'accélérer
l'acquision de certaines fonctionnalités en les
achetant. Un arbre technologique pourrait permettre d'effectuer les 
achats et récapituler la situation.
* Les acquisitions possibles concerneraient soit :
 - Déblocage d'un transmuteur (canaliser, refroidisseur...)
 - Ajout de fonctionnalités (enregistrement > 5 slots , pas a pas.
 ..)
 - Amélioration d'un transmuteur (canon à électron consommant 75% d'
 energie, positiveur chauffant moins...)
  
#### STRUCTURE/PROGRAMMATION
  
* Modifier la méthode d'accès aux variables "dat" & "art".
* Optimiser le code pour rendre l'usage d'OpenGL plus efficient.
* Repenser le mode simulation de façon orienté objet.
* Ajouter un makefile pour automatiser la construction du programme.
* Ajouter l'évènement "scroll,release" à la gestion des menus.
* Creer un gestionnaire de zones sensibles pour gérer le menu de 
selection des labos et les bulles d'aide.
  
#### STATISTIQUES

* Gérer le stockage des statistiques de victoire dans la base de donnée
  utilisateur.
* Ajouter les statistiques de victoire dans le menu principal.
* Ajouter les statistiques dans le mode simulation dans le dernier 
  panneau prévu à cet effet.
* Permettre la compilation et l'envoie de statistiques concernant le
  joueur vers le site internet de WireChem.
  
#### CONCEPTION
  
* Finir la conception du labo N°2.
  
#### FONCTIONNALITES
  
* Ajouter un mode création de labo/paillasses qui faciliterait l'ajout 
 et la configuration.
* Finir la fenêtre des préférences du jeu.
* Changer la forme du curseur lors de certaines actions.
* Utiliser la molette de la souris dans le jeu.
* Mettre en évidence les raccourcis clavier dans les bulles d'aide.
 
#### BOGUES

* Supprimer un bug d'activation selon le sens des photons.
* Supprimer le bug lorsque 2 électrons se croisent de face, ils rebond-
 issent.
* Corriger les bogues qui apparaissent parfois lors de l'usage des 
 transmuteurs "canaliseurs".
* Disparition du texte sous windows au bout de quelques minutes de jeu
 
#### DESIGN/MULTIMEDIA

* Créer des fonds plus attractifs pour le menu principal de choix de
 labo.
* Améliorer la qualité de la vidéo d'introduction.
* Enregistrer des vidéos de tutoriel pour chaque paillasse du niveau 1.
* Améliorer la qualités de l'accompagnement sonore & le diversifier.
* Ajouter des bruitages de jeu pour rendre les simulations plus immers-
  ives.
  
#### DOCUMENTATION/COMMUNICATION

* Améliorer les textes des documentations.
* Faire un logo ASCII art digne de ce nom.
  
