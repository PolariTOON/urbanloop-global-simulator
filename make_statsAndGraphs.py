from argparse import ArgumentParser, ArgumentTypeError # bibliothèque pour récupérer les arguments du main afin d'établir la simulation avec les paramètres en entrée
import matplotlib
import matplotlib.pyplot as plt
import math, os, glob, statistics
    

def make_global_graphs(durationInterval):        
    csvfileStats = open('stats/global/stat_log.csv', 'r')

    line = csvfileStats.readline()
    line = csvfileStats.readline()      # La ligne avec les noms de colonnes

    arrTime = [] 
    arrTravelersInAPod = []    
    arrWaitingTravelers = []              
    arrTravelingPods = []          

    arrTimeInInterval = [] 
    arrTravelersInAPodInInterval = []    
    arrWaitingTravelersInInterval = []              
    arrTravelingPodsInInterval = []          

    comptMinutes = 0
    
    while (line):
        arrLine = line.split(',')
        line = csvfileStats.readline()

        # On ajoute le time
        arrTimeInInterval.append(arrLine[0])

        # arrLine[2] contient "travelers in a pod" a un moment donne
        arrTravelersInAPodInInterval.append(int(arrLine[2]))

        # arrLine[3] contient "waiting travelers" a un moment donne
        arrWaitingTravelersInInterval.append(int(arrLine[3]))

        # arrLine[4] contient "traveling pods" a un moment donne
        arrTravelingPodsInInterval.append(int(arrLine[4]))

        comptMinutes += 1  

        if (comptMinutes == durationInterval):
            comptMinutes = 0
            arrTime.append(intervalOfListOfStringDates(arrTimeInInterval))

            # On ajoute les arrays de valeurs
            if (len(arrTravelersInAPodInInterval) > 0):
                arrTravelersInAPod.append(arrTravelersInAPodInInterval)
            else:           # Pas de valeurs ds l'array
                arrTravelersInAPod.append(0)
            
            if (len(arrWaitingTravelersInInterval) > 0):
                arrWaitingTravelers.append(arrWaitingTravelersInInterval)
            else:           # Pas de valeurs ds l'array
                arrWaitingTravelers.append(0)
            
            if (len(arrTravelingPodsInInterval) > 0):
                arrTravelingPods.append(arrTravelingPodsInInterval)
            else:           # Pas de valeurs ds l'array
                arrTravelingPods.append(0)

            arrTimeInInterval = [] 
            arrTravelersInAPodInInterval = []    
            arrWaitingTravelersInInterval = []              
            arrTravelingPodsInInterval = []       

    csvfileStats.close()

    make_boxplot(arrTime, arrTravelersInAPod, "Travelers in a pod", "stats/global/travelersInAPod")
    make_graph(arrTime, get_array_of_mean_from_array_of_array(arrTravelersInAPod), "Average travelers in a pod", "stats/global", "travelersInAPod_average", False)
    make_graph(arrTime, get_array_of_standard_deviation_from_array_of_array(arrTravelersInAPod), "Standard deviation travelers in a pod", "stats/global", "travelersInAPod_standardDeviation", False)

    make_boxplot(arrTime, arrWaitingTravelers, "Waiting Travelers", "stats/global/waitingTravelers")
    make_graph(arrTime, get_array_of_mean_from_array_of_array(arrWaitingTravelers), "Average waiting Travelers", "stats/global", "waitingTravelers_average", False)
    make_graph(arrTime, get_array_of_standard_deviation_from_array_of_array(arrWaitingTravelers), "Standard deviation waiting Travelers", "stats/global", "waitingTravelers_standardDeviation", False)

    make_boxplot(arrTime, arrTravelingPods, "Traveling Pods", "stats/global/travelingPods")
    make_graph(arrTime, get_array_of_mean_from_array_of_array(arrTravelingPods), "Average traveling Pods", "stats/global", "travelingPods_average", False)
    make_graph(arrTime, get_array_of_standard_deviation_from_array_of_array(arrTravelingPods), "Standard deviation traveling Pods", "stats/global", "travelingPods_standardDeviation", False)





def make_stations_graphs(durationInterval):
    files = glob.glob('stats/stations/*')
    for f in files:
        if (f != "stats/stations/infos.txt"):
            if (os.path.isdir(f)):
                filesInDirectory = glob.glob(f + "/*")
                for fileInDirectory in filesInDirectory:
                    if (fileInDirectory == (f + "/stats.csv")):
                        stationCsv = open(fileInDirectory, 'r')
                        # Creation et remplissage arrWaitingTime   
                        arrTime = [] 
                        arrWaitingTime = []

                        # Parsage
                        line = stationCsv.readline()
                        line = stationCsv.readline()

                        arrTimeInInterval = []
                        arrWaitingTimeInInterval = []
                        comptMinutes = 0

                        while (line):
                            arrLine = line.split(',')
                            line = stationCsv.readline()

                            # On ajoute le time
                            arrTimeInInterval.append(arrLine[0])

                            # On ajoute les valeurs contenues dans le tableau
                            arrLineOfArrLine = arrLine[1].split('|')     
                            for elt in arrLineOfArrLine:
                                if (elt != "" and elt != " " and elt != "\n" and elt != " \n"):
                                    arrWaitingTimeInInterval.append(float(elt))

                            comptMinutes += 1       

                            if (comptMinutes == durationInterval):
                                comptMinutes = 0
                                arrTime.append(intervalOfListOfStringDates(arrTimeInInterval))
                                # On ajoute les moyennes
                                if (len(arrWaitingTimeInInterval) > 0):
                                    arrWaitingTime.append(statistics.mean(arrWaitingTimeInInterval))
                                else:           # Pas de valeurs ds l'array
                                    arrWaitingTime.append(0)

                                arrTimeInInterval = []
                                arrWaitingTimeInInterval = []

                                # PS : si on veut afficher 10mn et qu'on regarde les intervalles de 3mn, on affichera pas la 10eme minute

                        make_graph(arrTime, arrWaitingTime, "Average waiting time", f, "waitingTime", False)
                        stationCsv.close()







def make_global_graph_with_global_csv_containing_stats_from_all_stations(durationInterval, filename, title):   # mettre bool pr conversion int/float ?
    csvfileStats = open("stats/global/" + filename + ".csv", 'r')

    line = csvfileStats.readline()      # Pas de ligne avec les noms de colonnes dans ces csv-la

    arrTime = [] 
    arrStat = []    
    arrTimeInInterval = [] 
    arrStatInInterval = [] 
      
    comptMinutes = 0
    
    while (line):
        arrLine = line.split(',')
        line = csvfileStats.readline()

        # On ajoute le time
        arrTimeInInterval.append(arrLine[0])

        # On ajoute les valeurs contenues dans le tableau
        for i in range(1, len(arrLine)):
            arrLineOfArrLine = arrLine[i].split('|')     
            for elt in arrLineOfArrLine:
                if (elt != "" and elt != " " and elt != "\n" and elt != " \n"):
                    arrStatInInterval.append(float(elt))

        comptMinutes += 1  

        if (comptMinutes == durationInterval):
            comptMinutes = 0
            arrTime.append(intervalOfListOfStringDates(arrTimeInInterval))

            # On ajoute les arrays de valeurs
            if (len(arrStatInInterval) > 0):
                arrStat.append(arrStatInInterval)
            else:           # Pas de valeurs ds l'array
                arrStat.append(0)

            arrTimeInInterval = [] 
            arrStatInInterval = []        

    csvfileStats.close()

    make_boxplot(arrTime, arrStat, title, "stats/global/" + filename)
    make_graph(arrTime, get_array_of_mean_from_array_of_array(arrStat), "Average " + title, "stats/global",  filename + "_average", False)
    make_graph(arrTime, get_array_of_standard_deviation_from_array_of_array(arrStat), "Standard deviation " + title, "stats/global", filename + "_standardDeviation", False)







def make_boxplot(array_time, array_of_array, title, filename):
    plt.boxplot(array_of_array)
    plt.title('Boxplot : ' + title)
    filename += "_boxplot.png"

    plt.gca().xaxis.set_ticklabels(array_time)

    plt.savefig(filename)
    # On clear la figure
    plt.clf()


def get_array_of_standard_deviation_from_array_of_array(array):
    arr_of_mean = []
    for elt in array:
        if (elt == 0):
            arr_of_mean.append(0)
        else:
            arr_of_mean.append(statistics.stdev(elt))
    return arr_of_mean


def get_array_of_mean_from_array_of_array(array):
    arr_of_mean = []
    for elt in array:
        if (elt == 0):
            arr_of_mean.append(0)
        else:
            arr_of_mean.append(statistics.mean(elt))
    return arr_of_mean


def make_graph(x, y, title, fileNamePref, fileNameSuf, isXComposedOfInt):
    plt.plot(x, y)
    plt.title(title)
    fileName = fileNamePref + "/" + fileNameSuf + ".png"

    if (isXComposedOfInt):
        yint = range(min(y), math.ceil(max(y))+1)
        plt.yticks(yint)

    plt.savefig(fileName)
    # On clear la figure
    plt.clf()


def intervalOfListOfStringDates(listOfStringDate):
    stringDate1 = listOfStringDate[0]                               # 8:00:00 
    stringDate2 = listOfStringDate[len(listOfStringDate) - 1]       # 8:02:00

    properDate1 = stringDate1[:-3]                                  # 8:00
    properDate2 = stringDate2[:-3]                                  # 8:02
    
    interval = properDate1 + "-" + properDate2                      # 8:00-8:02

    return interval


def delete_png_files_in_stats():
    files = glob.glob('stats/global/*')
    for f in files:
        if (f[-4:] != ".csv" and f[-4:] != ".txt"):          # On remove ce qui n'est pas un csv ou txt
            os.remove(f)
				
    files = glob.glob('stats/stations/*')
    for f in files:
        if (os.path.isdir(f)):
            # On supprime les fichiers dans le dossier
            filesInDirectory = glob.glob(f + "/*")
            for fileInDirectory in filesInDirectory:
                if (fileInDirectory[-4:] != ".csv"):          # On remove ce qui n'est pas un csv
                    os.remove(fileInDirectory)

    
def main(durationInterval):
    delete_png_files_in_stats()
    make_global_graphs(durationInterval)
    make_global_graph_with_global_csv_containing_stats_from_all_stations(durationInterval, "globalWaitingTime", "waiting time")
    make_stations_graphs(durationInterval)
    

if __name__ == "__main__":
    argument_parser = ArgumentParser(description="Run the making-stats_and_images script")
    argument_parser.add_argument("-i", "--durationInterval", type=int, default=30)
    arguments = argument_parser.parse_args()

    main(arguments.durationInterval)