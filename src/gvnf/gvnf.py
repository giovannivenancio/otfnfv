#!/usr/bin/env python

import os
import signal
from controller import *
from interface  import *
from utils      import exit_network

signal.signal(signal.SIGINT, exit_network)

if os.geteuid():
    print ("This program must run as root.")
    print ("Try: sudo gvnf")
    exit(1)

controller = Controller()
controller.start_network()

root = Tk()

def on_closing():
    controller.stop_network()

root.wm_title("OnTheFly VNF")

app = App(root, controller)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
