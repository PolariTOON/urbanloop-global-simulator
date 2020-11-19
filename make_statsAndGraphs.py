import matplotlib
import matplotlib.pyplot as plt
import math, os, glob
    

def makeStatsAndGraphs():
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

    makeGraph(arrTime, arrTravelersInAPod, "Number of travelers in a pod", "arrTravelersInAPod", True)
    makeGraph(arrTime, arrWaitingTravelers, "Number of waiting travelers", "arrWaitingTravelers", True)
    makeGraph(arrTime, arrTravelingPods, "Number of traveling pods", "arrTravelingPods", True)
    makeGraph(arrTime, arrAverageWaitingTime, "Average waiting time", "arrAverageWaitingTime", False)
    makeGraph(arrTime, arrAverageTravelTime, "Average travel time", "arrAverageTravelTime", False)
    makeGraph(arrTime, arrTotalGeneratedTravelers, "Total generated travelers", "arrTotalGeneratedTravelers", True)


def makeGraph(x, y, title, fileNameSuf, isXComposedOfInt):
    plt.plot(x, y)
    plt.title(title)
    fileName = "stats/global/" + fileNameSuf + ".png"

    if (isXComposedOfInt):
        yint = range(min(y), math.ceil(max(y))+1)
        plt.yticks(yint)

    if os.path.exists(fileName):
        os.remove(fileName)

    plt.savefig(fileName)
    # On clear la figure
    plt.clf()


    
def main():
    makeStatsAndGraphs()
    

if __name__ == "__main__":
    main()
