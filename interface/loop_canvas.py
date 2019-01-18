#! /usr/bin/env python3
# coding: utf-8

from tkinter import Canvas

class LoopCanvas(Canvas):
    def __init__(self,width,height,master):
        self.width = width
        self.height = height
        super().__init__(width=self.width, height=self.height, highlightthickness=0)
        self.master = master
    def update_selected_item(self, item):
        self.master.update_selected_item(item)