from tkinter import *
from tkinter import ttk

import math

from Field.FieldHandler import Field, Selectable, Cell, Room, Wall
from Field.PopulationHandler import Evolution
from Sensor.SensorHandler import Sensor, SensorField


class GUIHandler:

    def __init__(self):
        self._root = Tk()
        self._canvas = None
        self._init_properties()
        self._create_menu()
        self._create_main_frames(self._root)

        self._field = None
        self._sensor_field = None
        self._evolution = None
        self._generation_index = 0

    @staticmethod
    def _do_nothing():
        pass
        """
        filewin = Toplevel(self._root)
        button = Button(filewin, text="Do nothing button")
        button.pack()
        """

    def _init_properties(self):
        self._root.wm_title("SensorField v0.1")

    def _create_menu(self):
        menubar = Menu(self._root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self._do_nothing)
        filemenu.add_command(label="Open", command=self._do_nothing)
        filemenu.add_command(label="Save", command=self._do_nothing)
        filemenu.add_command(label="Save as...", command=self._do_nothing)
        filemenu.add_command(label="Close", command=self._do_nothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self._root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self._do_nothing)

        editmenu.add_separator()

        editmenu.add_command(label="Cut", command=self._do_nothing)
        editmenu.add_command(label="Copy", command=self._do_nothing)
        editmenu.add_command(label="Paste", command=self._do_nothing)
        editmenu.add_command(label="Delete", command=self._do_nothing)
        editmenu.add_command(label="Select All", command=self._do_nothing)

        menubar.add_cascade(label="Edit", menu=editmenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=self._do_nothing)
        helpmenu.add_command(label="About...", command=self._do_nothing)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self._root.config(menu=menubar)

    def run(self):
        self._update()
        self._root.mainloop()

    def _canvas_mouse_callback(self, event):
        if self._field is not None:
            self._field.notify(event)
        self._update()

    def _create_main_frames(self, parent):
        self._canvas = Canvas(parent, width=500, height=500)
        self._canvas.bind("<Button-1>", self._canvas_mouse_callback)
        tabs = self._create_tabs(parent)

        self._canvas.grid(row=0, column=0, rowspan=1, columnspan=1)
        tabs.grid(row=0, column=1, rowspan=1, columnspan=1, sticky=(N, S, W, E))

        parent.columnconfigure(0, weight=5)
        parent.columnconfigure(1, weight=5)
        parent.rowconfigure(0, weight=1)

    def _update(self):
        if self._selector_var.get() != 'Cell':
            self._btn_create_room.config(state=DISABLED)
        else:
            if len(Selectable.selected_elements):
                self._btn_create_room.config(state=NORMAL)
            else:
                self._btn_create_room.config(state=DISABLED)
        if self._selector_var.get() != 'Room':
            self._btn_delete_room.config(state=DISABLED)
            self._btn_merge_rooms.config(state=DISABLED)
        else:
            if len(Selectable.selected_elements):
                self._btn_delete_room.config(state=NORMAL)
            else:
                self._btn_delete_room.config(state=DISABLED)
            if len(Selectable.selected_elements) > 1:
                self._btn_merge_rooms.config(state=NORMAL)
            else:
                self._btn_merge_rooms.config(state=DISABLED)
        if self._selector_var.get() != 'Sensor':
            self._field.draw_pixels = False
            self._btn_delete_sensor.config(state=DISABLED)
        else:
            self._field.draw_pixels = True
            if len(Selectable.selected_elements):
                self._btn_delete_sensor.config(state=NORMAL)
            else:
                self._btn_delete_sensor.config(state=DISABLED)
        if self._selector_var.get() != 'Wall':
            self._btn_add_sensor.config(state=DISABLED)
        else:
            if len(Selectable.selected_elements):
                self._btn_add_sensor.config(state=NORMAL)
            else:
                self._btn_add_sensor.config(state=DISABLED)

        if self._evolution is not None:
            text = self._e_generations_var.get()
            if text.isnumeric() and text != '':
                index = int(text)
                if math.fabs(index) < len(self._evolution.generations):
                    self._generation_index = index
                else:
                    self._e_generations_var.set('')
                    self._generation_index = 0
            else:
                self._e_generations_var.set('')
                self._generation_index = 0

            self._lb_field.delete(0, self._lb_field.size())
            sorted_sensor_fields = self._evolution.get_generation(self._generation_index).get_sorted()
            for i, f in zip(range(len(sorted_sensor_fields)), sorted_sensor_fields):
                self._lb_field.insert(i, "Field "+str(i)+" cost: "+str(f.cost))

        if self._field.sensor_field is None:
            self._btn_refresh_sensors.config(state=DISABLED)
        else:
            self._btn_refresh_sensors.config(state=NORMAL)
        self._draw()

    def _create_tabs(self, parent):
        n = ttk.Notebook(parent)
        f1 = ttk.Frame(n, width=100)   # first page, which would get widgets gridded into it
        f2 = ttk.Frame(n)   # second page

        # f1
        self._selector_var = StringVar()
        self._selector_var.set("Cell")
        Label(f1, text="Select:").grid(row=0, column=0, sticky="nw")
        modes = [("Cells", "Cell", 1), ("Rooms", "Room", 2), ("Walls", "Wall", 3), ("Sensors", "Sensor", 4)]

        def sel():
            Selectable.remove_elements()
            Selectable.selector_target = self._selector_var.get()
            self._update()
        for t, v, i in modes:
            Radiobutton(f1, text=t, variable=self._selector_var,
                        value=v, command=sel).grid(row=i, column=0, sticky="nw")

        def create_room():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Cell):
                    if se.room_id == -1:
                        temp += [se.pos]
            if len(temp):
                self._field.create_new_room(temp)
                Selectable.remove_elements()
            self._update()
        self._btn_create_room = Button(f1, text='Create Room', width=30, command=create_room, state=DISABLED)
        grid_level = 5

        self._btn_create_room.grid(row=grid_level, column=0, sticky="nw")
        grid_level += 1

        def delete_room():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Room):
                    temp += [se]
            if len(temp):
                self._field.delete_room(temp)
                Selectable.remove_elements()
            self._update()
        self._btn_delete_room = Button(f1, text='Delete Room', width=30, command=delete_room, state=DISABLED)
        self._btn_delete_room.grid(row=grid_level, column=0, sticky="nw")
        grid_level += 1

        def merge_rooms():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Room):
                    temp += [se]
            if len(temp) > 1:
                cells = []
                # Create copy of cells
                for r in temp:
                    cells.extend(r.cells)
                # Delete rooms
                self._field.delete_room(temp)
                # Create one room to rule them all
                self._field.create_new_room(cells)
                Selectable.remove_elements()
            self._update()
        self._btn_merge_rooms = Button(f1, text='Merge Rooms', width=30, command=merge_rooms, state=DISABLED)
        self._btn_merge_rooms.grid(row=grid_level, column=0, sticky="nw")
        grid_level += 1

        def add_sensor():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Wall):
                    temp += [se]
            if len(temp):
                if self._field.sensor_field is None:
                    self._field.sensor_field = SensorField(field)
                for w in temp:
                    b = self._field.sensor_field.batches[w.room.id]
                    b.create_sensor_on(w)
                Selectable.remove_elements()
            self._update()
        self._btn_add_sensor = Button(f1, text='Add Sensor', width=30, command=add_sensor, state=DISABLED)
        self._btn_add_sensor.grid(row=grid_level, column=0, sticky="nw")
        grid_level += 1

        def delete_sensor():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Sensor):
                    temp += [se]
            if len(temp):
                # Delete sensor
                self._field.delete_sensors(temp)
                # Create one room to rule them all
                Selectable.remove_elements()
            self._update()
        self._btn_delete_sensor = Button(f1, text='Delete Sensor', width=30, command=delete_sensor, state=DISABLED)
        self._btn_delete_sensor.grid(row=grid_level, column=0, sticky="nw")
        grid_level += 1

        def refresh_sensors():
            if self._field.sensor_field is not None:
                self._field.sensor_field.check_room_sensors_visibility()
                self._update()
        self._btn_refresh_sensors = Button(f1, text='Refresh Sensors', width=30, command=refresh_sensors)
        self._btn_refresh_sensors.grid(row=grid_level, column=0, sticky="nw")
        grid_level += 1

        ################

        grid_level = 0

        def analyze_field():
            self._evolution = Evolution(self._field)
            self._lb_field.delete(0, self._lb_field.size())
            self._update()
        self._btn_analyze_field = Button(f2, text='Analyze Field', width=30, command=analyze_field)
        self._btn_analyze_field.grid(row=grid_level, column=0, columnspan=2, sticky="nw")
        grid_level += 1

        def generations_entry(_):
            self._update()

        self._e_generations_var = StringVar("")
        self._e_generations = Entry(f2, textvariable=self._e_generations_var)
        self._e_generations.bind('<Return>', generations_entry)
        Label(f2, text="Generation:").grid(row=grid_level, column=0, sticky="e")
        self._e_generations.grid(row=grid_level, column=1)
        grid_level += 1

        Label(f2, text="SelectField:").grid(row=grid_level, column=0, sticky="w")
        grid_level += 1

        def field_selected(evt):
            w = evt.widget
            if len(w.curselection()):
                index = int(w.curselection()[0])
                self._field.sensor_field = self._evolution.get_generation(self._generation_index).sensor_fields[index]
                self._field.sensor_field.check_room_sensors_visibility()
                self._update()

        self._sb_field = Scrollbar(f2)
        self._lb_field = Listbox(f2, height=20, width=35, selectmode=SINGLE)
        self._lb_field.bind('<<ListboxSelect>>', field_selected)
        self._lb_field.grid(row=grid_level, column=0, columnspan=2, sticky="nw")
        self._sb_field.grid(row=grid_level, column=2, sticky="nsw")
        self._lb_field.config(yscrollcommand=self._sb_field.set)
        self._sb_field.config(command=self._lb_field.yview)
        grid_level += 1

        n.add(f1, text='Create Field')
        n.add(f2, text='Analyze Field')
        return n

    def add_fields(self, f):
        self._field = f

    def _draw(self):
        # Draw cells
        self._field.draw(self._canvas)

if __name__ == "__main__":
    gui_handler = GUIHandler()
    field = Field()
    field.create_new_room([[2, 2], [2, 3], [3, 3]])
    field.create_new_room([[1, 1], [1, 2], [1, 3]])
    for batch in field.sensor_field.batches.values():
        room = batch.room
        for wall in room.walls:
            batch.create_sensor_on(wall)
    gui_handler.add_fields(field)
    gui_handler.run()

