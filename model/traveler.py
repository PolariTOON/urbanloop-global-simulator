from model import station


class Traveler:
    def __init__(self, departure_station_name, destination_station_name, waiting_since):
        """
         Travelers are automatically added to the queue in the departure_station
            :param departure_station_name: nom de la station de départ du voyageur (String)
            :param destination_station_name: nom de la station d'arrivée souhaitée par le voyageur (String)
            :param waiting_since: The time since the Traveler is waiting at departure_station (in seconds)
        """
        self.departure_station_name = departure_station_name
        self.departure_station_name = destination_station_name
        self.waiting_since = waiting_since
        departure_station = station.get_by_name(self.departure_station_name)
        departure_station.traveler_queue.put(self)
