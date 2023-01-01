import os
import tkinter as tk
import simulator
import sys

if __name__ == '__main__':
    dir_path = os.path.abspath(sys.argv[0])
    if os.path.isdir(dir_path):
        os.chdir(dir_path)
    else:
        os.chdir(os.path.dirname(dir_path))
    root = tk.Tk()
    a = simulator.Simulator(root)
    a.mainloop()
