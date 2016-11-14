import copy
import random

from Field.FieldHandler import cell_size


class Evolution:
    number_of_generations = 20
    number_of_fields = 30

    def __init__(self, field):
        self._base_field = field.create_copy()
        self._base_field.remove_sensors()
        self._generations = []
        self._current_time = 0
        self._init_first_generation()

    def _init_first_generation(self):
        first_generation = Generation()
        for gi in range(self.number_of_fields):
            print("Creating Field: ", gi)
            field_copy = self._base_field.create_copy()
            # add random sensors
            for room in field_copy.rooms.values():
                num_of_walls = len(room.walls)
                num_of_sensors = num_of_walls//3
                nos = random.randint(num_of_sensors-num_of_sensors//3, num_of_sensors+num_of_sensors//3)
                for s in range(nos):
                    wall = random.randint(0, num_of_walls-1)
                    pos = random.randint(1, cell_size-2)
                    alpha = random.random()*1.57-0.785
                    room.create_sensor_on(wall, pos, alpha)
            field_copy.check_room_sensors_visibility()
            field_copy.calculate_cost()
            first_generation.add_field(field_copy)
        self._generations += [first_generation]

    @property
    def generations(self):
        return self._generations

    def get_generation(self, i):
        return self._generations[i]


class Generation:
    def __init__(self):
        self._fields = []

    def add_field(self, field):
        self._fields += [field]

    @property
    def fields(self):
        return self._fields
