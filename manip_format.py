import json
import math

def upgrade_file(old_filename, new_filename):
        """
                Converts a file from the old format to the new network format
                (where stations are located on deviations instead of mini-loops)
        """
        with open(old_filename, 'r') as f:
                data = json.loads(f.read())
        upgrade_format(data)
        with open(new_filename, 'w') as f:
                f.write(pretty_dump(data, 2))

def pretty_dump(data, indent):
        """
            converts the dictionnary 'data' into a json text with
            tabulations of 2 spaces before main elements,
            but without adding "\n" for sections and elements.
            Ex:
              "name": "abc",
              "sections": [
                {"speed": 16.67, "path": {"type": "line"}},  <-  1 line / section
                {"speed": 16.67, "path": {"type": "line"}}
              ],
              ...
        """
        from copy import deepcopy
        import json

        # we are going to use json.dumps([...], indent=2) to create the json output,
        # except for data["loops"] and data["bridges"]

        result = ""

        # 1) use json.dump() on a fraction of 'data'
        sub_data = deepcopy(data)

        for key in data:
                if key in ["loops", "bridges"]:
                        del sub_data[key]

        result += json.dumps(sub_data, indent=indent)
        result = result[:-2] # remove final "\n}"
        
        # 1) adding "loops" and "bridges"

        def add_indent(text, indent):
                return "\n".join([ indent * ' ' + line for line in text.split('\n') ])
                
        def add_loop_or_bridge(loops_or_bridges, indent):
                """ @param indent: number of spaces before each line
                    @param loops_or_bridges: "loops" or "bridges"
                """
                
                def add_key_value(key, value, indent):
                        if key not in ["sections", "elements", "pods"]:
                                return "\"%s\": %s" % (key, json.dumps(value))
                        else:
                                result = ""
                                items = value
                                if len(items) == 0:
                                        result += "\"%s\": []" % key
                                else:
                                        result += "\"%s\": [\n" % key
                                        for i_item in range(len(items)):
                                                result += indent * " " + json.dumps(items[i_item])
                                                if i_item < len(items) - 1:
                                                        result += ","
                                                result += "\n"
                                        result += "]"
                                return result
                
                # we do everything without indents, and we add indents at the end
                result = ""
                for index in range(len(data[loops_or_bridges])):
                        loop_or_bridge = data[loops_or_bridges][index]
                        result += "{\n"
                        keys = list(loop_or_bridge.keys())
                        for i_key in range(len(keys)):
                                key = keys[i_key]
                                value = loop_or_bridge[key]
                                sub_json = add_key_value(key, value, indent)
                                result += add_indent(sub_json, indent)
                                if i_key < len(loop_or_bridge) - 1:
                                        result += ","
                                result += "\n"
                        result += "},\n" if index < len(data[loops_or_bridges]) - 1 else "}"
                
                # adding indents
                return result
        
        result += ",\n"

        loops_and_bridges = "\"loops\": [\n"
        loops_and_bridges += add_indent(add_loop_or_bridge("loops", indent), indent)
        loops_and_bridges += ("\n"
                              "],\n"
                              "\"bridges\": [\n")
        loops_and_bridges += add_indent(add_loop_or_bridge("bridges", indent), indent)
        loops_and_bridges += ("\n"
                              "]")

        result += add_indent(loops_and_bridges, indent)
        result += ("\n"
                   "}\n")
        
        return result

def upgrade_format(data):
        """
            Reçoit les données d'un réseau (telles qu'elles sont chargées depuis un json, c'est-à-dire des dictionnaires)
            dans l'ancien format (c'est-à-dire lorsque les stations/sheds ne pouvaient être pacés que sur des boucles
            et lorsque les bridges ne pouvaient contenir qu'une seule section).
            Modifie ces données pour qu'elles soient dans le nouveau format :
                - les bridges ont alors une liste de sections et d'éléments
                - les stations sont déplacées sur des bridges créés à l'occasion
        """
        from copy import deepcopy

        def calc_switches_coordinates(elem_coords, previous_coords, next_coords):
                """
                    calcule les coordonnées où placer les switches, en fonction de la position
                    de l'élément (station/shed) et de l'orientation de la route.
                    calcule aussi des nouvelles coordonnées pour l'élément, car celui-ci doit
                    être décalé hors de la route principale.
                """
                import math

                previous_direction = [ elem_coords[0] - previous_coords[0] , elem_coords[1] - previous_coords[1] ]
                next_direction     = [ next_coords[0] -     elem_coords[0] , next_coords[1] -     elem_coords[1] ]
                avg_direction = [ (previous_direction[i] + next_direction[i]) / 2 for i in range(2)]

                direction = [ avg_direction[i] / math.hypot(avg_direction[0], avg_direction[1]) for i in range(2) ] # normalize vector

                deviations_len = 10 # approximate length of each section between a switch and the station (actual length in [deviations_len/sqrt(2) ; deviations_len*sqrt(2)])

                len_on_loop = deviations_len * math.sqrt(2) # length of the section created between the switches
                
                switch_out_coords = [ elem_coords[i] - direction[i] * deviations_len/2 for i in range(2)]
                switch_in_coords  = [ elem_coords[i] + direction[i] * deviations_len/2 for i in range(2)]

                # we put the element at the exterior of the road's curvature, so we need to find the normal vector
                # going in the "exterior" of the road's curvature
                normal = [ - direction[1], direction[0] ]
                scalar_prod = normal[0] * previous_direction[0] + normal[1] * previous_direction[1]
                if scalar_prod < 0: # if 'normal' and 'previous_direction' are in opposite directions
                        normal = [ - normal[0], - normal[1] ]
                
                new_elem_coords = [ elem_coords[i] + normal[i] * deviations_len/2 for i in range(2) ]

                return new_elem_coords, switch_out_coords, switch_in_coords
        
        for b in data["bridges"]:
                b["sections"] = [ b["section"] ]
                b["elements"] = []
                del b["section"]
        
        for l in data["loops"]:
                i=0
                while i < len(l["elements"]):
                        # in case we need to move the element onto a bridge, we need to create 3 sections
                        # (2 sections for the bridge + 1 section between the 2 switches).
                        # we will copy the properties of the last section of the loop.
                        last_section = l["sections"][i-1] # we can use "i-1" because the first element is necessarily a switch (not a station/shed)
                        elem = l["elements"][i]
                        if elem["type"] in ["station", "shed"]:
                                # if we have a station/shed on the loop :
                                # 1) create a bridge and put
                                #    the station/shed on it
                                # 2) replace the station/shed on the loop by a
                                #    switchOut and a switchIn leading to that bridge
                                # 1)
                                new_bridge = {"name": "", "sections": [], "elements": [], "pods":[]}
                                new_bridge["name"] = "Deviation for " + elem["name"]
                                new_bridge["sections"].append(deepcopy(last_section)) # before station/shed
                                new_bridge["sections"].append(deepcopy(last_section)) # after station/shed
                                new_bridge["elements"].append(elem)
                                data["bridges"].append(new_bridge)
                                # 2)
                                id_bridge = data["bridges"].index(new_bridge)
                                # calculate coordinates
                                previous_elem = l["elements"][i-1] # i > 0 because there is a switch at i == 0
                                next_elem     = l["elements"][(i+1)%len(l["elements"])]
                                [elem["x"], elem["y"]], [x_out, y_out], [x_in, y_in] = calc_switches_coordinates(
                                        [          elem["x"],          elem["y"] ],
                                        [ previous_elem["x"], previous_elem["y"] ],
                                        [     next_elem["x"],     next_elem["y"] ]
                                )
                                # create switches
                                switch_out = {"type": "switch_out", "x": x_out, "y": y_out, "id_bridge": id_bridge, "pods": []}
                                switch_in = {"type": "switch_in", "x": x_in, "y": y_in, "id_bridge": id_bridge, "pods": []}
                                l["elements"][i] = switch_out # overwrite 'elem' that was moved onto the bridge
                                l["elements"].insert(i+1, switch_in)
                                l["sections"].insert(i+1, deepcopy(last_section)) #section between switch_out and switch_in
                        i += 1
        
        return

def create_mini_loops(data):
	""" Modifie les données d'un réseau (telles qu'elles sont chargées depuis un json (dans l'ancien format), c'est-à-dire des dictionnaires)
	    en remplaçant les stations et sheds par des mini-boucles, sur lesquels sont ensuite placés ces sheds/stations.
	    Cela était utilisé lorsqu'il était encore impossible de placer une station/shed autre part que sur une boucle,
	    afin de simuler les déviations des capsules qui accèdent à ces stations/sheds.
	"""
        
	if "modified" in data.keys():
		if data["modified"]:
			return data
	for loop in data["loops"]:
		if loop["name"] != " ":
			over = 0
			i = 0
			while over == 0:
				type = loop["elements"][i]["type"]
				if type == "station" or type == "shed":

					station_name = loop["elements"][i]["name"]
					pods = loop["elements"][i]["pods"]
					station_type = 0
					if type == "station":
						station_type = loop["elements"][i]["station_type"]
					bridge_name1 = " "
					bridge_name2 = " "

					loop_name = " "

					id_bridge = len(data["bridges"])

					x = loop["elements"][i]["x"]
					y = loop["elements"][i]["y"]

					#calcul des coordonnées pour les nouveaux éléments
					x_out1 = x #coordonnées du switch out qui va dans la nouvelle boucle
					y_out1 = y

					h1 = 20 #longueur des ponts
					h2 = 10#écart entre les 2 switchs de chaque boucle
					e = 15#écart entre les switchs de la nouvelle boucle et la station
					spd = 20#vitesse sur les sections inutilisées (pour changer la longueur des switchs)

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

					else:
						#angle entre la direction de la ligne et la verticale
						alpha = math.atan((x_suiv-x)/(y_suiv-y))

						x1 = h1 * math.cos(alpha)
						y1 = h1 * math.sin(alpha)
						x2 = h2 * math.sin(alpha)
						y2 = h2 * math.cos(alpha)

						beta = math.atan(2*e/h2)

						gamma = math.pi/2 - alpha - beta

						h3 = math.sqrt(math.pow((h2/2),2) + math.pow(e,2))

						x4 = h3 * math.cos(gamma)
						y4 = h3 * math.sin(gamma)

						if y_suiv > y:

							x_in2 = x_out1 + x1
							y_in2 = y_out1 - y1

							x_in1 = x_out1 + x2
							y_in1 = y_out1 + y2

							x_out2 = x_out1 + x1 + x2
							y_out2 = y_out1 + y2 - y1

							x_s = x_out1 + x1 + x4
							y_s = y_out1 - y1 + y4

						else :

							x_in2 = x_out1 - x1
							y_in2 = y_out1 + y1

							x_in1 = x_out1 - x2
							y_in1 = y_out1 - y2

							x_out2 = x_out1 - x1 - x2
							y_out2 = y_out1 - y2 + y1

							x_s = x_out1 - x1 - x4
							y_s = y_out1 + y1 - y4




					loop["elements"].pop(i)

					loop["elements"].insert(i, {"type": "switch_out", "x": x_out1, "y": y_out1, "id_bridge": id_bridge, "pods": [], "stat_or_shed": station_name})
					loop["elements"].insert(i+1, {"type": "switch_in", "x": x_in1, "y": y_in1, "id_bridge": id_bridge+1, "pods": []})


					loop["sections"].append(loop["sections"][0])

					data["bridges"].append({"name": bridge_name1, "section": {"speed": spd, "path": {"type": "line"}}, "pods": []},)
					data["bridges"].append({"name": bridge_name2, "section": {"speed": spd, "path": {"type": "line"}}, "pods": []},)

					if type == "station":

						data["loops"].append({"name": loop_name,
							"elements": [
								{"type": "switch_in", "x": x_in2, "y": y_in2, "id_bridge": id_bridge, "pods": []},
								{"type": "station", "name": station_name, "x": x_s, "y": y_s, "pods": pods, "station_type": station_type, "travelers": {"count": 0, "average_waiting_time": 0, "all_time_count": 0}},
								{"type": "switch_out", "x": x_out2, "y": y_out2, "id_bridge": id_bridge+1, "pods": []}
							],
							"sections": [
								{"speed": spd, "path": {"type": "line"}},
								{"speed": spd, "path": {"type": "line"}},
								{"speed": spd, "path": {"type": "line"}}
							],
							"pods": []
						})

					else:
						data["loops"].append({"name": loop_name,
							"elements": [
								{"type": "switch_in", "x": x_in2, "y": y_in2, "id_bridge": id_bridge, "pods": []},
        						{"type": "shed", "name": station_name, "x": x_s, "y": y_s, "pods": pods},
								{"type": "switch_out", "x": x_out2, "y": y_out2, "id_bridge": id_bridge+1, "pods": []}
							],
							"sections": [
								{"speed": spd, "path": {"type": "line"}},
								{"speed": spd, "path": {"type": "line"}, "weight": 10000},
								{"speed": spd, "path": {"type": "line"}}
							],
							"pods": []
						})

				i = i+1 
				if (i == len(loop["elements"])):
					over = 1
	data["modified"] = True
	s = open("sortie.json", "w")
	json.dump(data, s, sort_keys=True, indent=2)
	s.close()
	return data
