import random

import math

from Field.FieldHandler import cell_size
from Field.functions import choose_parents
from Sensor.SensorHandler import SensorField


class Evolution:
    number_of_generations = 20
    number_of_fields = 30
    number_of_elites = 4
    number_of_mutated_elites = 0

    sensor_delete_chance = 0.07
    sensor_create_chance = 0.07
    sensor_move_chance = 0.4
    max_sensor_delete = 3
    max_sensor_create = 3
    max_sensor_move = 3

    def __init__(self, field):
        self._base_field = field
        self._generations = []
        self._init_first_generation()

    def _init_first_generation(self):
        first_generation = Generation(self._base_field)
        for gi in range(self.number_of_fields):
            print("Creating Field: ", gi)
            sensor_field = SensorField(first_generation.field, str(len(self._generations))+str(gi))
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

    def create_next_generation(self):
        generation = Generation(self._base_field)
        prev_generation = self._generations[-1]
        sfs = prev_generation.get_sorted()
        # Adding elites to the next phase
        for i in range(self.number_of_elites):
            print("Creating Elite Field: ", i)
            generation.add_field(sfs[i])

        for i in range(self.number_of_mutated_elites):
            print("Creating Mutated Elite Field: ", i)

            sensor_field = SensorField(generation.field, str(len(self._generations)) + str(i), [sfs[i].field_id, ''])
            for batch in sensor_field.batches.values():
                for sensor in sfs[i].batches[batch.id].sensors:
                    batch.create_sensor_on(sensor.wall, sensor.pos, sensor.alpha)
                self._mutate(batch)
            sensor_field.check_room_sensors_visibility()
            sensor_field.calculate_cost()
            generation.add_field(sensor_field)

        costs = [s.cost for s in sfs[0:len(sfs)//3*2]]
        sum_cost = sum(costs)
        sfs_norm = [c/sum_cost for c in costs]
        sfs_norm = [math.sqrt(sum(sfs_norm[0:i])) for i in range(1, len(sfs_norm)+1)]
        # costs = [c-costs[0] for c in costs]

        # cost_max = prev_generation.get_cost_max()
        # reversed_cost_sum = prev_generation.get_reversed_cost_sum()
        # sfs_norm = [(cost_max-sf.cost) / reversed_cost_sum for sf in sfs]
        for i in range(self.number_of_fields - self.number_of_elites- self.number_of_mutated_elites):
            print("Creating Field: ", str(len(self._generations))+str(i))
            # choose parents p1, p2 - indices

            p1, p2 = choose_parents(sfs_norm)

            sensor_field = SensorField(generation.field, str(len(self._generations))+str(i), [sfs[p1].field_id,
                                                                                              sfs[p2].field_id])
            # add random sensors
            for batch in sensor_field.batches.values():
                batch_ps = []  # parent batches
                batch_ps += [sfs[p1].batches[batch.id]]
                batch_ps += [sfs[p2].batches[batch.id]]
                # pair - create division points

                temp = self._get_wall_genoms(batch_ps)

                for sensor in temp:
                    batch.create_sensor_on(sensor.wall, sensor.pos, sensor.alpha)
                # mutate
                # delete sensor
                while random.random() < self.sensor_delete_chance and len(batch.sensors) > 1:
                    s_id = random.randint(0, len(batch.sensors)-1)
                    batch.remove_sensor(s_id)
                    print("delete", sensor_field.field_id)
                # create sensor
                while random.random() < self.sensor_create_chance:
                    room = batch.room
                    num_of_walls = len(room.walls)
                    wall = random.randint(0, num_of_walls - 1)
                    pos = random.randint(1, cell_size - 2)
                    alpha = random.random() * 1.57 - 0.785
                    batch.create_sensor_on(wall, pos, alpha)
                    print("create", sensor_field.field_id)
                # move sensor
                while random.random() < self.sensor_move_chance:
                    s_id = random.randint(0, len(batch.sensors) - 1)
                    move = random.randint(0, 20)-10
                    rotate = random.random() * 0.698 - 0.349
                    sensor = batch.sensors[s_id]
                    sensor.move(move)
                    sensor.rotate(rotate)
                    print("move", sensor_field.field_id)

            sensor_field.check_room_sensors_visibility()
            sensor_field.calculate_cost()
            generation.add_field(sensor_field)

        self._generations += [generation]

    def _get_wall_genoms(self, batch_ps):
        temp = []  # to store the sensors

        temp_walls = batch_ps[0].room.walls

        p_s_temp = []

        for pi in range(2):
            p_s_temp += [[None for _ in range(len(temp_walls))]]
            for s in batch_ps[pi].sensors:
                for wi, w in zip(range(len(temp_walls)), temp_walls):
                    if w is s.wall:
                        p_s_temp[pi][wi] += [s]
        div = []
        same_as_parent = True
        while same_as_parent:
            div = [random.randint(0, 1) for _ in range(len(temp_walls))]  # 0010110000
            same_as_parent = all(t == 0 for t in div) or all(div)

        for wi in range(len(temp_walls)):
            for s in p_s_temp[div[wi]]:
                if s is not None:
                    temp += [s]
        return temp


    def _get_random_genoms(self, batch_ps):
        max_size = max(len(batch_ps[0].sensors), len(batch_ps[0].sensors))
        min_size = min(len(batch_ps[0].sensors), len(batch_ps[0].sensors))
        size = random.randint(min_size, max_size)

        div = []
        div += [0 for _ in range(len(batch_ps[0].sensors))]  # 000000
        div += [1 for _ in range(len(batch_ps[1].sensors))]  # 0000001111111

        same_as_parent = True
        start = 0
        sub = []
        if div != [0, 1]:
            random.shuffle(div)  # rotate it   011101011010101
            while same_as_parent:
                sub = div[start:start + size]
                same_as_parent = (all(t == 0 for t in sub) and size == len(batch_ps[0].sensors)) \
                                 or (all(sub) and size == len(batch_ps[1].sensors))
                start += 1
        else:
            sub = div

        temp = []
        p_s_temp = []
        p_s_temp += [[s for s in batch_ps[0].sensors]]  # sensors temp
        p_s_temp += [[s for s in batch_ps[1].sensors]]
        for p_id in sub:
            sensor = random.choice(p_s_temp[p_id])
            p_s_temp[p_id].remove(sensor)
            temp += [sensor]
        return temp

    def _mutate(self,  batch, c1=1, c2=1, c3=1):
        if random.random() * c1 < self.sensor_delete_chance and len(batch.sensors) > 1:
            s_id = random.randint(0, len(batch.sensors) - 1)
            batch.remove_sensor(s_id)
            print("delete")
        # create sensor
        if random.random() * c2 < self.sensor_create_chance:
            room = batch.room
            num_of_walls = len(room.walls)
            wall = random.randint(0, num_of_walls - 1)
            pos = random.randint(1, cell_size - 2)
            alpha = random.random() * 1.57 - 0.785
            batch.create_sensor_on(wall, pos, alpha)
            print("create")
        # move sensor
        if random.random() * c3 < self.sensor_move_chance:
            s_id = random.randint(0, len(batch.sensors) - 1)
            move = random.randint(0, 20) - 10
            rotate = random.random() * 0.698 - 0.349
            sensor = batch.sensors[s_id]
            sensor.move(move)
            sensor.rotate(rotate)
            print("move")

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

    def get_cost_max(self):
        cost_max = 0
        for sensor_field in self._sensors_fields:
            if cost_max < sensor_field.cost:
                cost_max = sensor_field.cost
        return cost_max

    def get_reversed_cost_sum(self):
        cost_reversed_sum = 0
        cost_max = self.get_cost_max()
        for sensor_field in self._sensors_fields:
            cost_reversed_sum += cost_max - sensor_field.cost
        return cost_reversed_sum
