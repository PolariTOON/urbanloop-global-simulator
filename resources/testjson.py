import json
import math


f = open("new-mini-network.json",'r')
data = json.load(f)

for loop in data["loops"]:
	if ("boucle station " in loop["name"]) == False:
		for i in range(len(loop["elements"])):
			if loop["elements"][i]["type"] == "station":

				station_name = loop["elements"][i]["name"]

				bridge_name1 = "entree " + station_name
				bridge_name2 = "sortie " + station_name

				loop_name = "boucle station " + station_name

				id_bridge = len(data["bridges"])

				x = loop["elements"][i]["x"]
				y = loop["elements"][i]["y"]

				#calcul des coordonnées pour les nouveaux éléments
				x_out1 = x #coordonnées du switch out qui va dans la nouvelle boucle
				y_out1 = y

				h1 = 25 #longueur des ponts
				h2 = 50#écart entre les 2 switchs de chaque boucle
				e = 15#écart entre les switchs de la nouvelle boucle et la station

				if i == len(loop["elements"]) - 1:
					elt_suiv = loop["elements"][0]
				else :
					elt_suiv = loop["elements"][i+1]

				#coordonnées de l'élément suivant
				x_suiv = elt_suiv["x"]
				y_suiv = elt_suiv["y"]

				
				if y_suiv == y :
					x_in2 = x_out1
					y_in2 = y_out1 + h1

					x_in1 = x_out1 - h2
					y_in1 = y_out1

					x_out2 = x_out1 - h2
					y_out2 = y_out1 + h1

					x_s = x_out1 - h2/2
					y_s = y_out1 + h1 + e

				else :
					#angle entre la direction de la ligne et la verticale
					alpha = math.atan((x_suiv-x)/(y_suiv-y))

					x1 = h1 * math.cos(alpha)
					y1 = h1 * math.sin(alpha)
					x2 = h2 * math.sin(alpha)
					y2 = h2 * math.cos(alpha)

					x_in2 = x_out1 + x1
					y_in2 = y_out1 - y1

					x_in1 = x_out1 + x2
					y_in1 = y_out1 + y2

					x_out2 = x_out1 + x1 + x2
					y_out2 = y_out1 + y2 - y1

					beta = math.atan(2*e/h2)

					gamma = alpha + beta - math.pi/4

					h3 = math.sqrt(math.pow((h2/2),2) + math.pow(e,2))

					x4 = h3 * math.cos(gamma)
					y4 = h3 * math.sin(gamma)

					x_s = x_out1 + x1 + x4
					y_s = y_out1 - y1 + y4

				loop["elements"].pop(i)

				loop["elements"].insert(i, {"type": "switch_out", "x": x_out1, "y": y_out1, "id_bridge": id_bridge, "pods": []})
				loop["elements"].insert(i+1, {"type": "switch_in", "x": x_in1, "y": y_in1, "id_bridge": id_bridge+1, "pods": []})


				loop["sections"].append(loop["sections"][0])

				data["bridges"].append({"name": bridge_name1, "section": {"speed": 6, "path": {"type": "line"}}, "pods": []},)
				data["bridges"].append({"name": bridge_name2, "section": {"speed": 6, "path": {"type": "line"}}, "pods": []},)

				data["loops"].append({"name": loop_name,
	      			"elements": [
	        			{"type": "switch_in", "x": x_in2, "y": y_in2, "id_bridge": id_bridge, "pods": []},
	        			{"type": "station", "name": station_name, "x": x_s, "y": y_s, "pods": {"max": 2, "count": 0}, "station_type": 0, "travelers": {"count": 0, "average_waiting_time": 0, "all_time_count": 0}},
	        			{"type": "switch_out", "x": x_out2, "y": y_out2, "id_bridge": id_bridge+1, "pods": []}
	      			],
	      			"sections": [
	        			{"speed": 7, "path": {"type": "line"}},
	        			{"speed": 7, "path": {"type": "line"}},
	        			{"speed": 7, "path": {"type": "line"}}
	      			],
	      			"pods": []
	    		})
				





s = open("sortie.json", "w")

json.dump(data, s,sort_keys=True, indent=2)


f.close()
s.close()