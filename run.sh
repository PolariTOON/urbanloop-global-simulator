#!/bin/bash

create(){
  curl -X POST -H "Content-Type:application/json" localhost:8090/new_trip -d "{ \"user_id\": \"123\", \"departure\": \"Gare\", \"arrival\": \"Velodrome\", \"typeCapsule\" : \"solo\" }"
}

infos(){
  curl localhost:8090/capsule/123
}

change(){
  curl -X POST -H "Content-Type:application/json" localhost:8090/change_dest -d "{ \"user_id\": \"123\", \"new_arrival\": \"Velodrome\" }"
}

emergency(){
  curl localhost:8090/emergency_exit/123
}

lavage(){
  curl -X POST -H "Content-Type:application/json" localhost:8090/envoi_lavage/123
}

revision(){
  curl -X POST -H "Content-Type:application/json" localhost:8090/envoi_revision/123
}

DefaultFunc(){
  launch
}

launch(){
  python3 main.py -p
}


if [ -z "$1" ]
then
    "DefaultFunc"
else
    if declare -f "$1" > /dev/null
    then
        # appel de la fonction en argument du script, et de ses paramÃ¨tres
        "$@"
    else
        # Le premier argument du script n'est pas une fonction
        echo "'$1' n'est pas le nom d'une fonction" >&2
        exit 1
    fi
fi