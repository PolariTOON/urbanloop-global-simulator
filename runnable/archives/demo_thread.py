import threading as thd
import time
import datetime as dt


def fun_th1():
    th = thd.current_thread()
    print(th.name)
    while True:
        print("[{0}][{1}] yo".format(dt.datetime.now().strftime("%H:%M:%S"), thd.get_ident()))
        time.sleep(1)


def fun_th2():
    th = thd.current_thread()
    print(th.name)
    while True:
        print("[{0}][{1}] mdr".format(dt.datetime.now().strftime("%H:%M:%S"), thd.get_ident()))
        time.sleep(5)


def main():
    th1 = thd.Thread(target=fun_th1)
    th2 = thd.Thread(target=fun_th2)
    th1.start()
    th2.start()
    return


main()
