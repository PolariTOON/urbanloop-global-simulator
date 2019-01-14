#! /usr/bin/env python3
# coding: utf-8

from tkinter import *
from tkinter import ttk

def create_window(w = 1200, h = 800):
    # creating a graphical app
    window = Tk()
    window["bg"] = "white"
    window.title = "URBANLOOP Simulator"

    # geometry of the app
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # configuring window grid
    window.rowconfigure(0, weight=1) # blank
    window.rowconfigure(1, weight=12) # content
    window.rowconfigure(2, weight=1) # blank
    window.columnconfigure(0, weight=1) # blank
    window.columnconfigure(1, weight=22) # content
    window.columnconfigure(2, weight=1) # blank
    
    # adding main_frame
    main_frame = Frame(window, relief=GROOVE, bg="green")
    main_frame.grid(column=1, row=1, sticky=N+S+E+W)

    # configuring main_frame grid
    main_frame.rowconfigure(0, weight=1) # single row
    main_frame.columnconfigure(0, weight=20) # simulator_frame
    main_frame.columnconfigure(1, weight=1) # blank
    main_frame.columnconfigure(2, weight=1) # separator
    main_frame.columnconfigure(3, weight=1) # blank
    main_frame.columnconfigure(4, weight=10) # information_frame

    # adding simulator_frame
    simulator_frame = Frame(main_frame, bg="orange")
    simulator_frame.grid(column=0, sticky=N+S+E+W)

    # adding vertical separator
    ttk.Separator(main_frame,orient=VERTICAL).grid(row=0, column=2, sticky=N+S)

    # adding information_frame
    information_frame = Frame(main_frame, bg="blue")
    information_frame.grid(row=0, column=4, sticky=N+S+E+W)

    return window
    #window.mainloop()

#window = create_window(800, 500)
#window.mainloop()