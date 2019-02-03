#! /usr/bin/env python3
# coding: utf-8

from tkinter import Tk, N, S, E, W, VERTICAL, Frame, Canvas
from tkinter import ttk, Menu, filedialog

from interface.simulator_frame import SimulatorFrame
from render.loop_renderer import LoopRenderer
from settings import network
from model import loop as ML


# créer une classe, c'est plus classe.
def create_window(w=1200, h=800, loop=None):  # TODO loop not used
    # creating a graphical app
    window = Tk()
    window["bg"] = "#e0e0e0"
    window.title("URBANLOOP Simulator")

    # geometry of the app
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # configuring window grid
    window.rowconfigure(0, weight=1)  # blank
    window.rowconfigure(1, weight=12)  # content
    window.rowconfigure(2, weight=1)  # blank
    window.columnconfigure(0, weight=1)  # blank
    window.columnconfigure(1, weight=22)  # content
    window.columnconfigure(2, weight=1)  # blank

    # add menu to window
    def open_file():
        file_path = filedialog.askopenfilename()
        network.load(file_path)
        lr = LoopRenderer(ML.all_loops[0], simulator_frame)
        lr.update_canvas()
        simulator_frame.canvas = lr.canvas
        # simulator_frame.grid(column=0, sticky=N+S+E+W)

    def open_example():
        network.load(None)  # load default network
        print(ML.all_loops[0])
        lr = LoopRenderer(ML.all_loops[0], simulator_frame)
        lr.update_canvas()
        simulator_frame.canvas = Canvas(simulator_frame)
        simulator_frame.canvas.pack()
        # simulator_frame.grid(column=0, sticky=N+S+E+W)

    menubar = Menu(window)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open file...", command=open_file)
    filemenu.add_command(label="Open example...", command=open_example)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=window.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    window.config(menu=menubar)

    # adding main_frame
    main_frame = Frame(window, bg="green")
    main_frame.grid(column=1, row=1, sticky=N + S + E + W)

    # configuring main_frame grid
    main_frame.rowconfigure(0, weight=1)  # single row
    main_frame.columnconfigure(0, weight=20)  # simulator_frame
    main_frame.columnconfigure(1, weight=1)  # blank
    main_frame.columnconfigure(2, weight=1)  # separator
    main_frame.columnconfigure(3, weight=1)  # blank
    main_frame.columnconfigure(4, weight=10)  # information_frame

    # adding simulator_frame
    # simulator_frame = Frame(main_frame, bg="orange")
    # simulator_frame.grid(column=0, sticky=N+S+E+W)
    simulator_frame = SimulatorFrame(master=main_frame)
    simulator_frame.grid(column=0, sticky=N + S + E + W)

    # adding vertical separator
    ttk.Separator(main_frame, orient=VERTICAL).grid(row=0, column=2, sticky=N + S)

    # adding information_frame
    information_frame = Frame(main_frame, bg="blue")
    information_frame.grid(row=0, column=4, sticky=N + S + E + W)

    return window

# window = create_window(800, 500)
# window.mainloop()
