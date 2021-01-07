# Simulateur global *UrbanLoop*

* Projet Industriel 2018-2019 de Mlle ASSELIN-BOULLÉ M. CHOCOT et M. HENRY encadré par M. Thibault CHOLEZ dont l'objectif est de créer un simulateur du réseau des capsules *UrbanLoop*.

* Projet Interdisciplinaire de la Découverte de la Recherche (2019) avec M. Frédéric VENIER et M. Victor THEVENON encadré par M. Thibault CHOLEZ dont l'objectif est l'amélioration du simulateur grâce à l'ajout du paradigme *SDN* (*Software Defined Networking*).

* Stages de deuxième année à *Telecom Nancy* effectués par M. Tristan LE GODAIS et M. Malo MONGARD encadrés par M. Thibault CHOLEZ dont les objectifs principaux sont l'amélioration du simulateur avec notamment l'ajout de l'algorithme d'aiguillage réalisé lors d'un autre Projet Industriel. Ces stages ont amené une refonte complète du simulateur.

* Projet Industriel 2019-2020 de M. GAU, M. OLIVIER et M. ALIBAY encadré par M. Thibault CHOLEZ dont l'objectif est de continuer le développement de la refonte du simulateur effectuée lors des précédents stages.

* Stage de deuxième année à *Telecom Nancy* effectué par M. Pierre-Antoine GROSSELIN encadré par M. Thibault CHOLEZ.

* Projet Industriel 2020-2021 de M. Clément CROUZET, M. Tristan DENIAU et M. Arthur SAOUT encadré par M. Thibault CHOLEZ dont l'objectif est de relier le simulateur avec les applications mobiles et des bornes de stations, ainsi que d'exploiter le simulateur pour obtenir des préconisations pour un réseau *UrbanLoop* à l'échelle du *Grand Nancy*.

## Contexte

Ce projet s'inscrit dans l'étude de la faisabilité du projet *UrbanLoop* dont l'objectif est d'effectuer un fort remaniement des transports en commun en milieu urbain avec une application dans l'agglomération du *Grand Nancy*.

Le sous-projet présent est :

* à la demande de Monsieur Jean-Philippe MANGEOT ;
* encadré par Monsieur Thibault CHOLEZ ;
* effectué par les élèves ingénieurs de *TELECOM Nancy* suivants :
	* Charlotte ASSELIN-BOULLÉ ;
	* Baptiste CHOCOT ;
	* Thibault HENRY ;
	* Victor THEVENON ;
	* Frederic VENIER ;
	* Tristan LE GODAIS ;
	* Malo MONGARD ;
	* Valentin GAU ;
	* Antoine OLIVIER ;
	* Dylan ALIBAY ;
	* Pierre-Antoine GROSSELIN ;
	* Clément CROUZET ;
	* Tristan DENIAU ;
	* Arthur SAOUT.

Le projet de ce dépôt s'inscrit dans le cadre scolaire d'un Projet Industriel de 3ème année à *TELECOM Nancy*. Le sujet est *Simulation du réseau de transport urbain par capsules UrbanLoop*.

Le sujet du Projet Interdispiplinaire de Découverte de la Recherche est *Amélioration du système de routage du simulateur d’UrbanLoop grâce au paradigme SDN*.

Les sujets des stages effectués sur le simulateur sont :
* *Interfaçage du simulateur global du réseau UrbanLoop avec celui des postes d’aiguillage* ;
* *Consolidation et extension du simulateur UrbanLoop*.

Le sujet du Projet Industriel de 3ème année est *Extension et amélioration du simulateur du réseau Urbanloop*.

## Contenu

Ce dépôt comprend différents dossiers et fichiers correspondant à la réalisation d'une maquette numérique simulant le réseau accompagnée de son interface utilisateur. Les éléments sont répartis suivant différents dossiers :

* [`documentation`](documentation) contient les différents documents pertinents pour la compréhension du projet ;
* [`model`](model) contient la majorité des classes d'objets et des fonctions liées (*Python*) ;
* [`view`](view) regroupe les éléments de l'interface graphique (*HTML* / *CSS* / *SVG* / *ECMAScript*) ;
* [`controler`](controler) contient les fichiers permettant de gérer la simulation et le modèle probabiliste ;
* [`resources`](resources) contient des exemples de réseaux au format *JSON*.
* [`test_project`](test_project) contient des classes et fonctions permettant de lancer plusieurs simulations de manière automatique.

## Usage

### Prérequis

* `python3.7`
* `pip3.7`

### Dépendances

* `simpy`
* `flask`
* `numpy`
* `scipy`

(voir `requirements.txt`)

Vous pouvez installer les dépendances avec :

```sh
$ pip3.7 install -r requirements.txt
```


### Lancement

Pour lancer le programme, utilisez :

```sh
$ python3.7 main.py -p
```

(l'utilisation préalable de `export FLASK_ENV=development` (ou `SET FLASK_ENV=development` sur Windows)
permet d'activer le mode debug de Flask).

Il est aussi possible de charger des réseaux dès le lancement :

```sh
$ python3.7 main.py -p -n path/to/network0.json path/to/network42.json
```

Ajouter le paramètre `-e` permet de supprimer tous les voyageurs de la simulation (utile pour tester l'application mobile) :

```sh
$ python3.7 main.py -e [...]
```

Utiliser `-d` permet de définir la durée à simuler, en secondes. Pour 24h :

```sh
$ python3.7 main.py -d 1440 [...]
```

Pour plus d'informations, utilisez la commande suivante :

```sh
$ python3.7 main.py -h
```

Il est possible de lancer plusieurs fois la même simulation via la commande:
```sh
$ python3.7 test_project/lauch_simulators.py -o True -r True -nb 10 -s 1 -p 8088 -n path/to/network0.json
```

Si l'option -o est désactivée, on peut lancer la commande:
```sh
$ python3.7 test_project\Simulations.py 8088 10
```
afin d'ouvrir les pages correspondant aux simulations lancées précédemment.

Pour plus d'informations, utilisez la commande suivante :

```sh
$ python3.7 test_project/lauch_simulators.py -h
```

Pour lancer le calcul de statistiques finales et creer les figures des statistiques temporelles dans le dossier stats/, utilisez :

```sh
$ python3.7 make_statsAndGraphs.py
```

Pour changer l'intervalle de temps (par defaut de 30 minutes), ajouter la commande -i et l'entier souhaite (5 par exemple) :

```sh
$ python3.7 make_statsAndGraphs.py -i 5
```

### Utilisation

L'interface se présente de la façon suivante :

![](pictures/1.png)

Pour visualiser un réseau il vous faut en charger un ; cliquez sur l'icône ![](pictures/load.png) puis sélectionnez le fichier *JSON* d'un réseau. Vous pouvez en avoir en exemple dans le dossier [`resources`](resources) de ce dépôt ou bien dans le [dépôt *GitLab* dédié](https://gitlab.telecomnancy.univ-lorraine.fr/urbanloop/r-seaux-json-pour-le-simulateur-global).

N'hésitez pas à y ajouter les réseaux que vous aurez créé.

Après cela, l'interface ressemblera à ceci :

![](pictures/int.png)

Vous pouvez lancer la simulation en cliquant sur le bouton ![](pictures/play.png).

Des informations sur les éléments du réseau sont disponibles lorsqu'ils sont séléctionnés via l'onglet [Data].

Vous pouvez visualiser ce qu'il se passe à un aiguillage lorsqu'il est sélectionné via l'onglet [Views] :

![](pictures/aig.png)

Avec le bouton ![](pictures/poubelle.png) vous pouvez supprimer le réseau choisi, pour ensuite en choisir un différent.

Pour se connecter à l'interface web depuis une autre machine du réseau local, il suffit d'accéder à \[IP hôte\]:\[port\] (\[IP hôte\] peut être obtenu avec `ipconfig` sur Windows et `ifconfig` sur Linux et Mac).

### API REST

Lorsque le programme est lancé avec l'interface web, le serveur Flask fournit également une API REST.

Cette API permet aux applications mobiles et des bornes de station d'intéragir avec le simulateur (par exemple pour qu'une demande de trajet sur les applications déclenche l'envoi d'une capsule dans le simulateur, et pour permettre à l'appli mobile de suivre la progression du trajet).

Pour utiliser l'API manuellement, vous pouvez par exemple utiliser `curl` (ici on prend l'exemple des stations de `resources/mini_network.json`) :

- création d'un voyageur :
	`curl -X POST -H "Content-Type:application/json" localhost:8090/new_trip -d "{ \"user_id\": \"123\", \"departure\": \"Stanislas\", \"arrival\": \"Telecom Nancy\", \"typeCapsule\" : \"solo\" }"`

- récupération des informations pour le suivi du trajet d'un voyageur d'id "123" :
	`curl localhost:8090/capsule/123`

- demande de changement de destination pour un voyageur d'id "123" :
	`curl -X POST -H "Content-Type:application/json" localhost:8090/change_dest -d "{ \"user_id\": \"123\", \"new_arrival\": \"Velodrome\" }"`

- demande de sortie d'urgence pour un voyageur d'id "123" :
	`curl localhost:8090/emergency_exit/123`


### Utilisation de *Docker*

#### Prérequis

* `docker`

#### Conteurisation

Le projet peut être embarqué dans un conteneur *Docker* en exécutant la commande suivante :

```sh
$ docker build -t urbanloop-simulator .
```

#### Lancement

Le conteneur peut ensuite être utilisé comme ceci (par exemple) :

```sh
docker run -itp 80:8090 --env n='resources/test2jerky.json' urbanloop-simulator
```

### Editeur

Pour utiliser l'éditeur, les instructions sont disponibles sur le ReadMe présent dans le dossier [`editeur_reseau`](editeur_reseau).
