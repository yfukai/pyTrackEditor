from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import functions as fn
from pyqtgraph import Point
import numpy as np

class ModifiedViewBox(pg.ViewBox):
    def __init__(self, parent=None, border=None, lockAspect=False, 
                 enableMouse=True, invertY=False, enableMenu=True, name=None, invertX=False):
        super().__init__(None, border, lockAspect, enableMouse, invertY, enableMenu, name, invertX)
        self.parent=parent