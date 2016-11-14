import math

from Field.FieldHandler import drawing_offset, cell_size, step_size, Selectable, d_m
from Field.functions import dist, set_l


class Sensor(Selectable):
    def __init__(self, wall, pos=cell_size//2, alpha=0):
        super(Sensor, self).__init__(color="#ff3300", selected_color="#00ffff")
        self._pos = pos  # middle of the wall
        self._alpha = alpha  # 0 means perpendicular to the wall, it is in radians
        self._wall = wall
        self._draw_radius = 3 * d_m
        self._select_radius = 6
        self._effect_radius = 40 * step_size # in step_size
        self._effect_arc = 0.5  # cos(60) = 0.5

        self._number_of_pixels = 0
        self._max_number_of_pixels = 1676

    @property
    def number_of_pixels(self):
        return self._number_of_pixels

    @number_of_pixels.setter
    def number_of_pixels(self, value):
        self._number_of_pixels = value

    @property
    def max_number_of_pixels(self):
        return self._max_number_of_pixels

    @property
    def room_id(self):
        return self._wall.room_id

    @property
    def effect_radius(self):
        return self._effect_radius

    @property
    def effect_arc(self):
        return self._effect_arc

    def get_look_dir(self):
        wall_normal = [[0, 1], [-1, 0], [0, -1], [1, 0]]
        v = wall_normal[self._wall.orientation]
        return [math.cos(self._alpha)*v[0]+math.sin(self._alpha)*v[1],
                -math.sin(self._alpha)*v[0]+math.cos(self._alpha)*v[1]]

    def get_pos(self):
        # Right corner if looking inward
        x1 = self._wall.corners[0].pos[1] * cell_size
        y1 = self._wall.corners[0].pos[0] * cell_size

        sensor_pos_rel2wall = [[step_size, 0], [0, -step_size], [-step_size, 0], [0, step_size]]
        sensor_pos_on_wall = [[0, self._pos], [self._pos, 0], [0, -self._pos], [-self._pos, 0]]
        x = x1 + sensor_pos_on_wall[self._wall.orientation][1]+sensor_pos_rel2wall[self._wall.orientation][1]
        y = y1 + sensor_pos_on_wall[self._wall.orientation][0] + sensor_pos_rel2wall[self._wall.orientation][0]
        return [x, y]

    def draw(self, canvas):
        pos = [p * d_m + drawing_offset for p in self.get_pos()]
        v = set_l(self.get_look_dir(), 15 * d_m)
        canvas.create_line(pos[0], pos[1], pos[0] + v[0], pos[1] + v[1], fill=self.color, width=self.width)
        canvas.create_oval(pos[0] - self._draw_radius, pos[1] - self._draw_radius,
                           pos[0] + self._draw_radius, pos[1] + self._draw_radius, fill=self.color)

    def point_is_inside(self, m_x, m_y):
        pos = self.get_pos()
        return dist(pos, [m_x, m_y]) < self._select_radius
