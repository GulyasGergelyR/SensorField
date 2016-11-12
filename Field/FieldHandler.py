from collections import OrderedDict
from tkinter import ALL

size = 10
cell_size = 20
step_size = 1

drawing_offset = 20

class Selectable:
    selected = []
    only1allowed = False
    selector_target = Cell.__name__

    def __init__(self, color="#6984c9", selected_color="#3607ea"):
        self._selected = False
        self._color = color
        self._selected_color = selected_color
        self._width = 2
        self._selected_width = 4

    def select(self, b=True):
        if self.only1allowed:
            for s in self.selected:
                s.selected = False
            self.selected = []

        if self.__class__.__name__ == self.selector_target and b:
            self._selected = True
            Selectable.selected += [self]
        elif self in Selectable.selected:
            self._selected = False
            Selectable.selected.remove(self)

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


class Field:
    def __init__(self):
        self._corners = [[Corner(i, j) for j in range(size+1)] for i in range(size+1)]
        self._cells = [[Cell(i, j, [self._corners[i + n//2][j + n % 2] for n in [0, 1, 3, 2]])
                        for j in range(size)] for i in range(size)]
        self._corners = []
        self._rooms = OrderedDict()

    @property
    def cells(self):
        return self._cells

    @property
    def rooms(self):
        return self._rooms

    def notify(self, event):
        m_x = event.x
        m_y = event.y
        if Selectable.selector_target == Cell.__name__:
            for row in self._cells:
                for cell in row:
                    if cell.point_is_inside(m_x, m_y):
                        cell.select()
        if Selectable.selector_target == Room.__name__:
            for room in self._rooms.values():
                if room.point_is_inside(m_x, m_y):
                    room.select()

    def create_new_room(self, cells):
        r_id = 1
        while r_id in self._rooms.keys():
            r_id += 1
        room = Room(self, r_id)
        room.add_cells(cells)
        self.init_walls_in(room)
        self._rooms[r_id] = room

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
            self._connect_walls_in(room)

    def _connect_walls_in(self, room):
        for wall in room.walls:
            for w in room.walls:
                if wall != w:
                    if wall.try_to_connect(w):
                        break

    def draw(self, canvas):
        canvas.delete(ALL)
        # Draw cells
        self._draw_cells(canvas)
        # Draw grid and walls
        self._draw_grid_and_walls(canvas)

    def _draw_cells(self, canvas):
        for row in self._cells:
            for cell in row:
                cell.draw(canvas)

    def _draw_grid_and_walls(self, canvas):
        x = drawing_offset
        y = drawing_offset
        for i in range(size+1):
            canvas.create_line(x + i * cell_size, y, x + i * cell_size, y+size*cell_size, fill="#1f5a56")
            canvas.create_line(x, y + i * cell_size, x + size * cell_size, y + i * cell_size, fill="#1f5a56")

        for room in self._rooms.values():
            for wall in room.walls:
                wall.draw(canvas)


class Room(Selectable):
    def __init__(self, field, new_id, color="#000066", selected_color="#0066ff"):
        super(Room, self).__init__(color, selected_color)
        self._id = new_id
        self._walls = []
        self._cells = []
        self._field = field

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
        return any([cell.point_is_inside(m_x, m_y)] for cell in self._cells)


class Cell(Selectable):
    def __init__(self, i, j, corners, color="#006666", selected_color="#0066ff"):
        super(Cell, self).__init__(color, selected_color)
        self._room_id = -1
        self._room = None
        self._pos = [i, j]
        self._sides = [None, None, None, None]
        self._corners = corners

    def add_wall(self, wall):
        self._sides[wall.orientation] = wall

    def get_corners_at(self, o):
        # Left upper - 0, Right upper - 1, Right bottom - 2, Left bottom - 3
        return [self._corners[o], self._corners[(o+1) % 4]]

    def draw(self, canvas):
        x = drawing_offset + self._pos[1] * cell_size
        y = drawing_offset + self._pos[0] * cell_size
        canvas.create_rectangle(x, y, x+cell_size, y+cell_size, fill=self.color)

    def point_is_inside(self, m_x, m_y):
        x = drawing_offset + self._pos[1] * cell_size
        y = drawing_offset + self._pos[0] * cell_size

        return x < m_x < x+cell_size and y < m_y < y+ cell_size

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
        print("id: "+str(room.id))
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


class Wall(Selectable):
    def __init__(self, cell, o):
        super(Wall, self).__init__(color="#009900", selected_color="#00ff00")
        self._orientation = o
        self._corners = cell.get_corners_at(o)
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

    def draw(self, canvas):
        x1 = drawing_offset + self._corners[0].pos[1] * cell_size
        y1 = drawing_offset + self._corners[0].pos[0] * cell_size
        x2 = drawing_offset + self._corners[1].pos[1] * cell_size
        y2 = drawing_offset + self._corners[1].pos[0] * cell_size
        canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.width)


class Door:
    def __init__(self):
        self._e2l = None  # element to the left
        self._e2r = None  # element to the right
