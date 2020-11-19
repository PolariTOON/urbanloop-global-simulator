from argparse import ArgumentParser, ArgumentTypeError # bibliothèque pour récupérer les arguments du main afin d'établir la simulation avec les paramètres en entrée
import matplotlib
import matplotlib.pyplot as plt
import math, os, glob, statistics
    

def make_stats_and_graphs():        #PRENDRE EN COMPTE LA PERIODE (exple 30mn)
    csvfileStats = open('stats/global/stat_log.csv', 'r')
    csvfileFinalStats = open('stats/global/final_stat_log.csv', 'w')

    line = csvfileStats.readline()
    line = csvfileStats.readline()      # La ligne avec les noms de colonnes
    maxTravelersInAPod = 0              # Le nombre maximal de voyageurs qu'il y a eu a un moment donne dans les capsules
    maxWaitingTravelers = 0              
    maxTravelingPods = 0            

    arrTravelersInAPod = []    # Array contenant le nb de voyageurs qu'il y a eu dans les capsules au cours de la simul
    arrWaitingTravelers = []              
    arrTravelingPods = []        
    arrAverageWaitingTime = []              
    arrAverageTravelTime = []       
    arrTotalGeneratedTravelers = []       

    arrTime = [] 
    
    while (line):
        arrLine = line.split(',')
        line = csvfileStats.readline()

        # On ajoute le time
        arrTime.append(arrLine[0])

        # arrLine[2] contient "travelers in a pod" a un moment donne
        arrTravelersInAPod.append(int(arrLine[2]))
        if (int(arrLine[2]) > maxTravelersInAPod):
            maxTravelersInAPod = int(arrLine[2])

        # arrLine[3] contient "waiting travelers" a un moment donne
        arrWaitingTravelers.append(int(arrLine[3]))
        if (int(arrLine[3]) > maxWaitingTravelers):
            maxWaitingTravelers = int(arrLine[3])

        # arrLine[4] contient "traveling pods" a un moment donne
        arrTravelingPods.append(int(arrLine[4]))
        if (int(arrLine[4]) > maxTravelingPods):
            maxTravelingPods = int(arrLine[4])

        # arrLine[5] contient "traveling pods" a un moment donne
        arrAverageWaitingTime.append(float(arrLine[5]))

        # arrLine[6] contient "traveling pods" a un moment donne
        arrAverageTravelTime.append(float(arrLine[6]))

        # arrLine[7] contient "traveling pods" a un moment donne
        arrTotalGeneratedTravelers.append(int(arrLine[7]))
    
    csvfileFinalStats.write('Maximum travelers in a pod, Maximum waiting travelers, Maximum traveling pods\n')
    csvfileFinalStats.write(str(maxTravelersInAPod) + ", ")
    csvfileFinalStats.write(str(maxWaitingTravelers) + ", ")
    csvfileFinalStats.write(str(maxTravelingPods) + ", ")

    csvfileStats.close()
    csvfileFinalStats.close()

    make_graph(arrTime, arrTravelersInAPod, "Number of travelers in a pod", "stats/global", "arrTravelersInAPod", True)
    make_graph(arrTime, arrWaitingTravelers, "Number of waiting travelers", "stats/global", "arrWaitingTravelers", True)
    make_graph(arrTime, arrTravelingPods, "Number of traveling pods", "stats/global", "arrTravelingPods", True)
    make_graph(arrTime, arrAverageWaitingTime, "Average waiting time", "stats/global", "arrAverageWaitingTime", False)
    make_graph(arrTime, arrAverageTravelTime, "Average travel time", "stats/global", "arrAverageTravelTime", False)
    make_graph(arrTime, arrTotalGeneratedTravelers, "Total generated travelers", "stats/global", "arrTotalGeneratedTravelers", True)


def make_graph(x, y, title, fileNamePref, fileNameSuf, isXComposedOfInt):
    plt.plot(x, y)
    plt.title(title)
    fileName = fileNamePref + "/" + fileNameSuf + ".png"

    if (isXComposedOfInt):
        yint = range(min(y), math.ceil(max(y))+1)
        plt.yticks(yint)

    if os.path.exists(fileName):
        os.remove(fileName)

    plt.savefig(fileName)
    # On clear la figure
    plt.clf()



def make_stations_graphs(durationInterval):
    files = glob.glob('stats/stations/*')
    for f in files:
        if (f != "stats/stations/infos.txt"):
            if (os.path.isdir(f)):
                filesInDirectory = glob.glob(f + "/*")
                for fileInDirectory in filesInDirectory:
                    if (fileInDirectory == (f + "/stats.csv")):
                        stationCsv = open(fileInDirectory, 'r')
                        # Creation et remplissage arrAverageWaitingTime   
                        arrTime = [] 
                        arrAverageWaitingTime = []

                        # Parsage
                        line = stationCsv.readline()
                        line = stationCsv.readline()

                        arrTimeInInterval = []
                        arrAverageWaitingTimeInInterval = []
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
                                    arrAverageWaitingTimeInInterval.append(float(elt))

                            comptMinutes += 1       

                            if (comptMinutes == durationInterval):
                                comptMinutes = 0
                                arrTime.append(intervalOfListOfStringDates(arrTimeInInterval))
                                # On ajoute les moyennes
                                if (len(arrAverageWaitingTimeInInterval) > 0):
                                    arrAverageWaitingTime.append(statistics.mean(arrAverageWaitingTimeInInterval))
                                else:           # Pas de valeurs ds l'array
                                    arrAverageWaitingTime.append(0)
                                arrTimeInInterval = []
                                arrAverageWaitingTimeInInterval = []

                                # PS : si on veut afficher 10mn et qu'on regarde les intervalles de 3mn, on affichera pas la 10eme minute

                        make_graph(arrTime, arrAverageWaitingTime, "Average waiting time", f, "arrAverageWaitingTime", False)
                        stationCsv.close()



def intervalOfListOfStringDates(listOfStringDate):
    stringDate1 = listOfStringDate[0]                               # 8:00:00 
    stringDate2 = listOfStringDate[len(listOfStringDate) - 1]       # 8:02:00

    properDate1 = stringDate1[:-3]                                  # 8:00
    properDate2 = stringDate2[:-3]                                  # 8:02
    
    interval = properDate1 + "-" + properDate2                      # 8:00-8:02

    return interval

    
def main(durationInterval):
    make_stats_and_graphs()
    make_stations_graphs(durationInterval)
    

if __name__ == "__main__":
    argument_parser = ArgumentParser(description="Run the making-stats_and_images script")
    argument_parser.add_argument("-i", "--durationInterval", type=int, default=30)
    arguments = argument_parser.parse_args()

    main(arguments.durationInterval)