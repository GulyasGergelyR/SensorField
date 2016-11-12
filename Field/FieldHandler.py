from collections import OrderedDict

import Tkinter

size = 64


class Field:
    def __init__(self):
        self._corners = [[Corner(i, j) for i in range(size+1)] for j in range(size+1)]
        self._cells = [[Cell(i, j, [self._corners[i+n//2][j+n % 2] for n in range(4)])
                        for i in range(size)] for j in range(size)]
        self._corners = []
        self._rooms = OrderedDict()

    def add_room(self, room):
        self._rooms[room.id] = room

    def get_room(self, r_id):
        if r_id in self._rooms.keys():
            return self._rooms[r_id]
        return None

    def init_walls(self):
        self._create_walls()
        self._connect_walls()

    def _create_walls(self):
        for r_id, room in self._rooms.iteritems():
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
                        Wall(cell, 0)
                if p[1] < size-1:
                    if self._cells[p[0]][p[1]].room_id != self._cells[p[0]][p[1]+1].room_id:
                        Wall(cell, 2)

    def _connect_walls(self):
        for room in self._rooms:
            for wall in room.walls:
                for w in room.walls:
                    if wall != w:
                        if wall.try_to_connect(w):
                            break


class Room:
    def __init__(self, new_id):
        self._id = new_id
        self._walls = []
        self._cells = []

    def add_wall(self, wall):
        self._walls += [wall]

    def add_cell(self, cell):
        self._cells += [cell]
        cell.room = self

    @property
    def cells(self):
        return self._cells

    @property
    def walls(self):
        return self._walls

    @property
    def id(self):
        return self._id


class Cell:
    def __init__(self, i, j, corners):
        self._room_id = 0
        self._room = None
        self._pos = [i, j]
        self._sides = [None, None, None, None]
        self._corners = corners

    def add_wall(self, wall):
        self._sides[wall.orientation] = wall

    def get_corners_at(self, o):
        # Left upper - 0, Right upper - 1, Right bottom - 2, Left bottom - 3
        return [self._corners[o], self._corners[(o+1) % 3]]

    @property
    def room_id(self):
        return self._room_id

    @property
    def pos(self):
        return self._pos

    @property
    def room(self):
        return self._room

    @room.setter
    def room(self, room):
        self._room = room
        self._room_id = room.id


class Corner:
    def __init__(self, i, j):
        self._pos = [i, j]


class Wall:
    def __init__(self, cell, o):
        self._cell = cell
        self._orientation = o
        self._corners = cell.get_corners_at(o)
        cell.add_wall(self)
        cell.room.add_wall(self)
        self._e2l = None  # element to the left
        self._e2r = None  # element to the right

        self._sensors = []

    def try_to_connect(self, wall):
        # walls looking inward - corner[0] is always at the right hand side
        if self._corners[0] in wall.corners:
            self._e2r = wall
            wall._e2l = self
            return True
        elif self._corners[1] in wall.corners:
            self._e2l = wall
            wall._e2r = self
            return True
        return False

    @property
    def orientation(self):
        return self._orientation

    @property
    def corners(self):
        return self._corners

    @property
    def e2l(self):
        return self._e2l

    @property
    def e2r(self):
        return self._e2r


class Door:
    def __init__(self):
        self._e2l = None  # element to the left
        self._e2r = None  # element to the right
