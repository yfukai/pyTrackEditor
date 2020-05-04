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

class ClickDrawableImageItem(pg.ImageItem):
    def __init__(self,image=None,kernel=np.ones((3,3),dtype=np.bool),**kwargs):
        super().__init__(image,**kwargs)
        self.drawing=False
        self.setDrawKernel(kernel=kernel,mode="set")

    def hoverEvent(self, event):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        event.acceptClicks(QtCore.Qt.RightButton)
        #XXX using mouseMoveEvent may be better, but I couldn't figure out how to call setMouseTracking...
        if self.drawing:
            self.poss.extend([event.lastPos(),event.pos()])
            self.drawAt(event.pos())

    def mouseClickEvent(self, event):
        print("mouseclick")
        if event.button() & QtCore.Qt.RightButton:
            if self.drawing:
                self.endDraw()
                self.drawing=False
            else:
                self.drawing=True
                self.poss=[]
    
    def endDraw(self):
        print(self.poss)