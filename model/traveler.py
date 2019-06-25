from model import identifier
from simulator import sim_loop


class Traveler:
    def __init__(self, departure_station, destination_station):
        """
        Travelers are automatically added to the queue in the departure_station
        :param departure_station_name: nom de la station de départ du voyageur (String)
        :param destination_station_name: nom de la station d'arrivée souhaitée par le voyageur (String)
        :param waiting_since: The time since the Traveler is waiting at departure_station (in seconds)
        """
        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_traveler_id()
        self.departure_station = departure_station
        self.destination_station = destination_station
        self.waiting_since = sim_loop.get_current_tick()
        self.trip_start_tick = None
        self.departure_station.traveler_queue.put(self)

    def stats(self):
        from model import controller
        controller.get_controller().temps_moy_voy_stat(self.id, sim_loop.get_simulated_time())

    def get_waiting_seconds(self):
        """
        :return: The waiting time in seconds
        """
        if self.trip_start_tick is None:
            return int(sim_loop.get_simulated_time() - sim_loop.get_simulated_time(self.waiting_since))
        return int(sim_loop.get_simulated_time(self.trip_start_tick) - sim_loop.get_simulated_time(self.waiting_since))
