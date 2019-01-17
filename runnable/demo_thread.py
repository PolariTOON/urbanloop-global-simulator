#! /usr/bin/env python3
# coding: utf-8

from threading import Thread
import time
import datetime as dt

def fun_th1():
    while True:
        print("[{0}] yo".format(dt.datetime.now().strftime("%H:%M:%S")))
        time.sleep(1)

def fun_th2():
    while True:
        print("[{0}] mdr".format(dt.datetime.now().strftime("%H:%M:%S")))
        time.sleep(5)

def main():
    th1 = Thread(target=fun_th1)
    th2 = Thread(target=fun_th2)
    th1.start()
    th2.start()
    return

main()