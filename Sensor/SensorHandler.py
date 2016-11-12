from Field.FieldHandler import Selectable, drawing_offset, cell_size

step_size = 0.1


class Sensor(Selectable):
    def __init__(self, wall):
        super(Sensor, self).__init__()
        self._pos = 0.5  # middle of the wall
        self._alpha = 0  # 0 means perpendicular to the wall, it is in radians
        self._wall = wall

    def pos(self):
        x1 = drawing_offset + self._wall.corners[0].pos[1] * cell_size
        y1 = drawing_offset + self._wall.corners[0].pos[0] * cell_size
        x2 = drawing_offset + self._wall.corners[1].pos[1] * cell_size
        y2 = drawing_offset + self._wall.corners[1].pos[0] * cell_size

        x = x1 + (x2 - x1) * self._pos
        y = y1 + (y2 - y1) * self._pos
        return [x, y]

    def draw(self):
        pass


