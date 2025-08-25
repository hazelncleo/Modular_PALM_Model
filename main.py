import numpy as np
import matplotlib.pyplot as plt
import os
import json
import glob
from shutil import copy2 as copy_input_file
from shutil import rmtree
import inquirer
from tkinter import Tk
from tkinter.filedialog import askdirectory
import string
from Modular_Abaqus_Builder import Modular_Abaqus_Builder

def main():
    

    # Instantiate class
    model = Modular_Abaqus_Builder()

    model.main_loop()


if __name__ == '__main__':
    main()