#!/bin/bash
curl -X POST -H "Content-Type:application/json" localhost:8090/change_dest -d "{ \"user_id\": \"123\", \"new_arrival\": \"$1\" }"
