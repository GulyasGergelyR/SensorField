from collections import OrderedDict
from tkinter import ALL

from Field.functions import *

size = 15
cell_size = 20
step_size = 1

drawing_offset = 20
d_m = 2
d_cell_size = cell_size * d_m


class Selectable:
    selected_elements = []
    only1allowed = False
    selector_target = 'Cell'

    def __init__(self, color="#6984c9", selected_color="#3607ea"):
        self._selected = False
        self._color = color
        self._selected_color = selected_color
        self._width = 2
        self._selected_width = 4

    def select(self, b=True):
        if self.only1allowed:
            for s in self.selected_elements:
                s.selected = False
            self.selected_elements = []

        if self.__class__.__name__ == self.selector_target and b:
            self._selected = True
            Selectable.selected_elements += [self]
        elif self in Selectable.selected_elements:
            self._selected = False
            Selectable.selected_elements.remove(self)

    @staticmethod
    def remove_elements():
        for se in Selectable.selected_elements:
            se._selected = False
        Selectable.selected_elements = []

    @property
    def color(self):
        if self._selected:
            return self._selected_color
        return self._color

    @property
    def width(self):
        if self._selected:
            return self._selected_width
        return self._width

    @property
    def selected(self):
        return self._selected


class Field:
    def __init__(self):
        self._corners = [[Corner(i, j) for j in range(size+1)] for i in range(size+1)]
        self._cells = [[Cell(i, j, [self._corners[i + n//2][j + n % 2] for n in [0, 1, 3, 2]])
                        for j in range(size)] for i in range(size)]
        self._pixels = [[Pixel(i, j, self._cells[i//cell_size][j//cell_size])
                        for j in range(int(size*cell_size/step_size))]
                        for i in range(int(size*cell_size/step_size))]

        self._corners = []
        self._rooms = OrderedDict()

        self.draw_pixels = False

        from Sensor.SensorHandler import SensorField
        self._sensors_field = SensorField(self)

    def create_copy(self):
        field = Field()
        for room in self._rooms.values():
            cells = [cell.pos for cell in room.cells]
            field.create_new_room(cells, room.id)

        return field

    @property
    def sensor_field(self):
        return self._sensors_field

    @sensor_field.setter
    def sensor_field(self, value):
        self._sensors_field = value

    @property
    def cells(self):
        return self._cells

    @property
    def rooms(self):
        return self._rooms

    @property
    def pixels(self):
        return self._pixels

    def notify(self, event):
        m_x = (event.x - drawing_offset) / d_m
        m_y = (event.y - drawing_offset) / d_m
        if Selectable.selector_target == 'Cell':
            for row in self._cells:
                for cell in row:
                    if cell.point_is_inside(m_x, m_y):
                        cell.select(not cell.selected)
        if Selectable.selector_target == 'Room':
            for room in self._rooms.values():
                if room.point_is_inside(m_x, m_y):
                    room.select(not room.selected)
        if Selectable.selector_target == 'Sensor':
            if self._sensors_field is not None:
                for batch in self._sensors_field.batches.values():
                    for sensor in batch.sensors:
                        if sensor.point_is_inside(m_x, m_y):
                            sensor.select(not sensor.selected)
        if Selectable.selector_target == 'Wall':
            for room in self._rooms.values():
                if room.point_is_inside(m_x, m_y):
                    temp = []
                    for wall in room.walls:
                        if wall.point_is_inside(m_x, m_y):
                            temp += [wall]
                    d = cell_size+1
                    w = None
                    for wall in temp:
                        distance = wall.dist_from(m_x, m_y)
                        w = wall if distance < d else w
                        d = distance if distance < d else d
                    if w is not None:
                        w.select(not w.selected)

    def create_new_room(self, cells, new_r_id=None):
        if new_r_id is None:
            r_id = 1
            while r_id in self._rooms.keys():
                r_id += 1
        else:
            r_id = new_r_id
        room = Room(self, r_id)
        room.add_cells(cells)
        self.init_walls_in(room)
        self._rooms[r_id] = room
        self._sensors_field.create_new_batch(room)

    def delete_room(self, rooms):
        for room in rooms:
            if room in self._rooms.values():
                self._rooms.pop(room.id)
                for cell in room.cells:
                    cell.remove_room()
            if self._sensors_field is not None:
                self._sensors_field.remove_batch(room.id)

    def delete_sensors(self, sensors):
        if self._sensors_field is not None:
            for sensor in sensors:
                batch = self._sensors_field.batches[sensor.room_id]
                batch.remove_sensor(sensor)

    def delete_all(self):
        if self._sensors_field is not None:
            for batch in self._sensors_field.batches.values():
                batch.delete_all()

    def get_room(self, r_id):
        if r_id in self._rooms.keys():
            return self._rooms[r_id]
        return None

    def init_walls(self):
        self._create_walls()
        self._connect_walls()

    def init_walls_in(self, room):
        self._create_walls_in(room)
        self._connect_walls_in(room)

    def _create_walls(self):
        for room in self._rooms.values():
            self._create_walls_in(room)

    def _create_walls_in(self, room):
        room.delete_walls()
        for cell in room.cells:
            # Check directions
            p = cell.pos
            # Up - 0, Right - 1, Down - 2, Left - 3

            if p[0] > 0:
                if self._cells[p[0]][p[1]].room_id != self._cells[p[0]-1][p[1]].room_id:
                    Wall(cell, 0)
            if p[0] < size-1:
                if self._cells[p[0]][p[1]].room_id != self._cells[p[0]+1][p[1]].room_id:
                    Wall(cell, 2)
            if p[1] > 0:
                if self._cells[p[0]][p[1]].room_id != self._cells[p[0]][p[1]-1].room_id:
                    Wall(cell, 3)
            if p[1] < size-1:
                if self._cells[p[0]][p[1]].room_id != self._cells[p[0]][p[1]+1].room_id:
                    Wall(cell, 1)

    def _connect_walls(self):
        for room in self._rooms:
            room.connect_walls()

    @staticmethod
    def _connect_walls_in(room):
        room.connect_walls()

    def draw(self, canvas):
        canvas.delete(ALL)
        # Draw cells
        self._draw_cells(canvas)
        # Draw grid and walls
        if self.draw_pixels:
            self._draw_pixels(canvas)
        self._draw_grid_and_walls(canvas)
        self._draw_sensors(canvas)

    def _draw_cells(self, canvas):
        for row in self._cells:
            for cell in row:
                cell.draw(canvas)

    def _draw_grid_and_walls(self, canvas):
        x = drawing_offset
        y = drawing_offset
        for i in range(size+1):
            #canvas.create_line(x + i * d_cell_size, y, x + i * d_cell_size, y + size * d_cell_size, fill="#1f5a56")
            #canvas.create_line(x, y + i * d_cell_size, x + size * d_cell_size, y + i * d_cell_size, fill="#1f5a56")
            pass

        for room in self._rooms.values():
            for wall in room.walls:
                wall.draw(canvas)

    def _draw_sensors(self, canvas):
        if self._sensors_field is not None:
            for batch in self._sensors_field.batches.values():
                for sensor in batch.sensors:
                    sensor.draw(canvas)

    def _draw_pixels(self, canvas):
        for room in self._rooms.values():
            for cell in room.cells:
                for pixel in cell.pixels:
                    pixel.draw(canvas)


class Room(Selectable):
    def __init__(self, field, new_id, color="#000066", selected_color="#0066ff"):
        super(Room, self).__init__(color, selected_color)
        self._id = new_id
        self._walls = []
        self._cells = []
        self._field = field
        self._pixels = []

        self._polygon = []
        self._wall_functions = []

    @property
    def polygon(self):
        return self._polygon

    @property
    def wall_functions(self):
        return self._wall_functions

    def connect_walls(self):
        for wall in self._walls:
            for w in self._walls:
                if wall != w:
                    if wall.try_to_connect(w):
                        break
        self._create_polygon()

    def _create_polygon(self):
        self._wall_functions = []
        self._polygon = []
        w_temps = [self._walls[0]]
        for i in range(1, len(self._walls)):
            w_temps += [w_temps[-1].e2r]
        self._polygon += [w_temp.corners[1].get_pos() for w_temp in w_temps]
        for i in range(len(self._polygon)):
            self._wall_functions += [function(self._polygon[i], self._polygon[(i + 1) % len(self._polygon)])]

    def add_wall(self, wall):
        self._walls += [wall]

    def add_cells(self, cells):
        # cells has to be a tuple of Cell or [int, int]
        for cell in cells:
            if isinstance(cell, (tuple, list)):
                cell = self._field.cells[cell[0]][cell[1]]
            if isinstance(cell, Cell):
                self._cells += [cell]
                cell.room = self
            else:
                raise TypeError("Wrong type from cell")

    @property
    def cells(self):
        return self._cells

    @property
    def walls(self):
        return self._walls

    @property
    def id(self):
        return self._id

    def delete_walls(self):
        self._walls = []

    def point_is_inside(self, m_x, m_y):
        return any([cell.point_is_inside(m_x, m_y) for cell in self._cells])


class Cell(Selectable):
    def __init__(self, i, j, corners, color="#006666", selected_color="#0066ff"):
        super(Cell, self).__init__(color, selected_color)
        self._room_id = -1
        self._room = None
        self._pos = [i, j]
        self._corners = corners

        self._pixels = []

    @property
    def pixels(self):
        return self._pixels

    def add_pixel(self, pixel):
        self._pixels += [pixel]

    def remove_room(self):
        self._room = None
        self._room_id = -1
        for p in self._pixels:
            p.number_of_sensors = 0

    def get_corners_at(self, o):
        # Left upper - 0, Right upper - 1, Right bottom - 2, Left bottom - 3
        return [self._corners[o], self._corners[(o+1) % 4]]

    def draw(self, canvas):
        x = drawing_offset + self._pos[1] * cell_size * d_m
        y = drawing_offset + self._pos[0] * cell_size * d_m
        canvas.create_rectangle(x, y, x+d_cell_size, y+d_cell_size, fill=self.color)

    def point_is_inside(self, m_x, m_y):
        x = self._pos[1] * cell_size
        y = self._pos[0] * cell_size
        return x < m_x < x+cell_size and y < m_y < y + cell_size

    @property
    def room_id(self):
        return self._room_id

    @property
    def pos(self):
        return self._pos

    def get_pos(self):
        x = self._pos[1] * cell_size
        y = self._pos[0] * cell_size
        return [x, y]

    @property
    def room(self):
        return self._room

    @room.setter
    def room(self, room):
        self._room = room
        self._room_id = room.id

    @property
    def color(self):
        if self._selected:
            return self._selected_color
        elif self._room is not None:
            return self._room.color
        return self._color


class Corner:
    def __init__(self, i, j):
        self._pos = [i, j]

    @property
    def pos(self):
        return self._pos

    def get_pos(self):
        return [self._pos[1]*cell_size, self._pos[0]*cell_size]


class Pixel:
    def __init__(self, i, j, cell):
        self._cell = cell
        cell.add_pixel(self)
        self._pos = [i, j]
        self._number_of_sensors = 0

    def get_pos(self):
        base_pos = self._cell.get_pos()
        return [base_pos[0] + (self._pos[1] % cell_size/step_size) * step_size, base_pos[1]
                + (self._pos[0] % cell_size/step_size) * step_size]

    def check_sensor_visibility2(self, field, sensor):
        sp = sensor.get_pos()
        pp = self.get_pos()

        v = [pp[0] - sp[0], pp[1] - sp[1]]

        if dist(sp, pp) > sensor.effect_radius or a(v, sensor.get_look_dir()) < sensor.effect_arc:
            return

        # TODO add other step size compatibility

        # Check pixels in between if valid room point or a wall
        for r in range(int(dist(sp, pp)/step_size)):
            v_temp = set_l(v, (r+1)*step_size)
            temp_p = [sp[0]+int(v_temp[0]), sp[1]+int(v_temp[1])]
            pixel = field.pixels[temp_p[1]][temp_p[0]]
            if pixel.room_id != sensor.room_id:
                break
        else:
            self._number_of_sensors += 1

    def check_sensor_visibility(self, batch, sensor):
        sp = sensor.get_pos()
        pp = self.get_pos()
        v = [pp[0] - sp[0], pp[1] - sp[1]]
        if dist(sp, pp) > sensor.effect_radius or a(v, sensor.get_look_dir()) < sensor.effect_arc:
            return  # if farther then effect radius or not in effect arc
        v_f = function(sp, pp)  # create function for ray
        for f in batch.room.wall_functions:  # get function for wall
            if functions_intersect(f, v_f):
                break
        else:
            self._number_of_sensors += 1
            sensor.number_of_pixels += 1

    def draw(self, canvas):
        color = "#ff"
        level = 255-self._number_of_sensors*40
        color += '{0:02X}00'.format(level if level > 0 else 0)
        if self._number_of_sensors > 0:
            pos = [p * d_m + drawing_offset for p in self.get_pos()]
            for d_mi in range(d_m):
                canvas.create_line(pos[0], pos[1] + d_mi, pos[0]+1 * d_m, pos[1] + d_mi, fill=color)

    @property
    def number_of_sensors(self):
        return self._number_of_sensors

    @property
    def room_id(self):
        return self._cell.room_id

    @number_of_sensors.setter
    def number_of_sensors(self, value):
        self._number_of_sensors = value


class Wall(Selectable):
    def __init__(self, cell, o):
        super(Wall, self).__init__(color="#009900", selected_color="#00ff00")
        self._orientation = o
        self._corners = cell.get_corners_at(o)
        cell.room.add_wall(self)
        self._room = cell.room
        self._cell = cell
        self._e2l = None  # element to the left
        self._e2r = None  # element to the right

    def try_to_connect(self, wall):
        # walls looking inward - corner[0] is always at the right hand side
        if self._corners[0] in wall.corners:
            self._e2r = wall
            wall._e2l = self
            return True
        """
        if self._corners[1] in wall.corners:
            self._e2l = wall
            wall._e2r = self
            print()
            return True
        """
        return False

    @property
    def orientation(self):
        return self._orientation

    @property
    def corners(self):
        return self._corners

    @property
    def room(self):
        return self._room

    @property
    def room_id(self):
        return self._room.id

    @property
    def e2l(self):
        return self._e2l

    @property
    def e2r(self):
        return self._e2r

    def get_pos(self):
        x1 = self._corners[0].pos[1] * cell_size
        y1 = self._corners[0].pos[0] * cell_size
        x2 = self._corners[1].pos[1] * cell_size
        y2 = self._corners[1].pos[0] * cell_size
        return [[x1, y1], [x2, y2]]

    def draw(self, canvas):
        x1 = drawing_offset + self._corners[0].pos[1] * cell_size * d_m
        y1 = drawing_offset + self._corners[0].pos[0] * cell_size * d_m
        x2 = drawing_offset + self._corners[1].pos[1] * cell_size * d_m
        y2 = drawing_offset + self._corners[1].pos[0] * cell_size * d_m
        canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.width)

    def dist_from(self, m_x, m_y):
        p = self.get_pos()
        p = [(p[0][0] +p [1][0]) / 2, (p[0][1] + p[1][1]) / 2]
        return dist(p, [m_x, m_y])

    def point_is_inside(self, m_x, m_y):
        return self._cell.point_is_inside(m_x, m_y)


class Door:
    def __init__(self):
        self._e2l = None  # element to the left
        self._e2r = None  # element to the right
