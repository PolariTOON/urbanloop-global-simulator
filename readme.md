# PI_2018-19_urbanloop

* Projet Industriel 2018-2019 de Mlle ASSELIN-BOULLÉ M CHOCOT et M HENRY encadré par M CHOLEZ dont l'objectif est de créer un simulateur du réseau des capsules URBANLOOP.

* Projet Interdisciplinaire de la Découverte de la Recherche (2019) avec M Frédéric VENIER et M Victor THEVENON encadré par M CHOLEZ dont l'objectif est l'amélioration du simulateur grâce à l'ajout du paradigme SDN (Software Defined Networking).

* Stages de deuxième année à Telecom Nancy effectués par M Tristan LE GODAIS et M Malo MONGARD encadrés par M CHOLEZ dont les objectifs principaux sont l'amélioration du simulateur avec notamment l'ajout de l'algorithme d'aiguillage réalisé lors d'un autre Projet Industriel. Ces stages ont amené une refonte complète du simulateur.

## Contexte

Ce projet s'inscrit dans l'étude de la faisabilité du Projet URBANLOOP dont l'objectif est d'effectuer un fort remaniement des transports en commun en milieu urbain avec une application dans la Métropole Nancéenne.
Le sous projet présent est  
* à la demande de Monsieur Jean-Philippe MANGEOT
* encadré par Monsieur Thibault CHOLEZ

effectué par les élèves ingénieurs de TELECOM Nancy suivants :
* Charlotte ASSELIN-BOULLÉ
* Baptiste CHOCOT
* Thibault HENRY
* Victor THEVENON
* Frederic VENIER
* Tristan LE GODAIS
* Malo MONGARD

Le projet de ce repôt s'inscrit dans le cadre scolaire d'un Projet Industriel de 3ème année à TELECOM Nancy. Le sujet est _*Simulation du réseau de Transport Urbain par capsules URBANLOOP*_

Le sujet du Projet Interdispiplinaire de découverte de la recherche est _*Amélioration du système de routage du simulateur d’Urbanloop grâce au paradigme SDN*_

Les sujets des stages efféctués sur le simulateur sont :
* _*Interfaçage du simulateur global du réseau UrbanLoop avec celui des postes d’aiguillage*_
* _*Consolidation et extension du simulateur Urbanloop*_

## Contenu
Ce repot comprend différents dossiers et fichiers correspondant à la réalisation d'une maquette numérique simulant le réseau accompagnée de son interface utilisateur. Les éléments sont répartis suivant différents dossiers :
* **documentation** contient les différents Documents pertinent pour la compréhension du projet.
* **model** contient la majorité des classes d'objets et des fonctions liées (Python).
* **view** regroupe les éléments de l'interface graphique (JavaScript/HTML/CSS/SVG).
* **controler** contient les fichiers permettant de gérer la simulation et le modèle probabiliste.
* **resources** contient des exemples de réseau au format JSON.

## Usage
### Prérequis
* Python3.7


### Lancement
Pour lancer le programme (après téléchargement des sources) compiler et exécuter en ligne de commande :

```
python3.7 main.py -p
```

Pour plus d'informations, utilisez la commande :

```
python3.7 main.py -h
```



### Dépendances
* ```simpy```
* ```flask```

### Utilisation

L'interface se présente de la façon suivante :
![](pictures/1.png)

Pour visualiser un réseau il vous faut en charger un, cliquez sur l'icône ![](pictures/load.png) puis sélectionnez le fichier JSON d'un réseau. Vous pouvez en avoir en exemple dans le dossier resources du repot ou sur ce dépôt git :
https://gitlab.telecomnancy.univ-lorraine.fr/urbanloop/r-seaux-json-pour-le-simulateur-global

N'hésitez pas à y ajouter les réseaux que vous aurez créé.

Après cela, l'interface resssemblera à ceci :
![](pictures/int.png)

Vous pouvez lancer la simulation en cliquant sur le bouton ![](pictures/play.png)

Des informations sur les éléments du réseau sont disponibles lorsqu'ils sont séléctionnés via l'onglet 'Data'.

Vous pouvez visualiser ce qu'il se passe à un aiguillage lorsqu'il est sélectionné via l'onglet 'View' ![](pictures/aig.png)

Avec le bouton ![](pictures/poubelle.png) vous pouvez supprimer le réseau choisi, pour ensuite en choisir un différent.