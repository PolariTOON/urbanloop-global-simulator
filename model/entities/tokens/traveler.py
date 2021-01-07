from .token import Token


class Traveler(Token):
    def __init__(self, env, generation_time=None, waiting_time=None, boarding_time=None, real_user=False, **kwargs):
        super().__init__(env, **kwargs)
        self._waiting_time = waiting_time or 0
        self._generation_time = generation_time or 0
        self._boarding_time = boarding_time or 5
        self._real_user = real_user
        self._changed_dest = False
        self._called_emergency_exit = False   

    @property
    def name(self):
        return super().name or "Traveler %s" % self.id

    @property
    def waiting_time(self):
        return self._waiting_time

    @classmethod
    def boarding_time(self):
        return self._boarding_time

    @property
    def boarding_time(self):
        return self._boarding_time
        
    @property
    def real_user(self):
        return self._real_user

    @property
    def changed_dest(self):
        return self._changed_dest

    @property
    def called_emergency_exit(self):
        return self._called_emergency_exit

    def departure(self, time):
        self._waiting_time = time - self._generation_time
        return self._waiting_time

    def serialize(self):
        dict = super().serialize()
        return dict

    def update(self):
        return

    def handle_message(self, message):
        return

    def change_destination(self):
        self._changed_dest = True

    def call_emergency_exit(self):
        self._called_emergency_exit = True   
