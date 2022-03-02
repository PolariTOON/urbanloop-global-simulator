#!/bin/bash
curl -X POST -H "Content-Type:application/json" localhost:8090/new_trip -d "{ \"user_id\": \"123\", \"departure\": \"Telecom Nancy\", \"arrival\": \"$1\", \"typeCapsule\" : \"solo\" }"



