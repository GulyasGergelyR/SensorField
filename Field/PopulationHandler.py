import copy
import random

from Field.FieldHandler import cell_size
from Sensor.SensorHandler import SensorField


class Evolution:
    number_of_generations = 20
    number_of_fields = 30

    def __init__(self, field):
        self._base_field = field
        self._generations = []
        self._init_first_generation()

    def _init_first_generation(self):
        first_generation = Generation(self._base_field)
        for gi in range(self.number_of_fields):
            print("Creating Field: ", gi)
            sensor_field = SensorField(first_generation.field)
            # add random sensors
            for batch in sensor_field.batches.values():
                room = batch.room
                num_of_walls = len(room.walls)
                num_of_sensors = num_of_walls//3
                nos = random.randint(num_of_sensors-num_of_sensors//3, num_of_sensors+num_of_sensors//3)
                for s in range(nos):
                    wall = random.randint(0, num_of_walls-1)
                    pos = random.randint(1, cell_size-2)
                    alpha = random.random()*1.57-0.785
                    batch.create_sensor_on(wall, pos, alpha)
            sensor_field.check_room_sensors_visibility()
            sensor_field.calculate_cost()
            first_generation.add_field(sensor_field)
        self._generations += [first_generation]

    def _init_next_generation(self):
        generation = Generation(self._base_field)

        self._generations += [generation]

    @property
    def generations(self):
        return self._generations

    def get_generation(self, i):
        return self._generations[i]


class Generation:
    def __init__(self, field):
        self._field = field
        self._sensors_fields = []

    def add_field(self, sensor_field):
        self._sensors_fields += [sensor_field]

    @property
    def field(self):
        return self._field

    @property
    def sensor_fields(self):
        return self._sensors_fields

    def get_sorted(self):
        return sorted(self._sensors_fields, key=lambda x: x.cost)
